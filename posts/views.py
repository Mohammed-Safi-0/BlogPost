from django.shortcuts import render, redirect, get_object_or_404
from .forms import *
from .models import BlogPost, PostImage, category as Category, Reaction, Report, Comment
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count
from django.core.paginator import Paginator
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import JsonResponse, StreamingHttpResponse, Http404
import logging
from django.views.decorators.http import require_POST
from .summarizer import generate_summary


def home(request):
    selected_category = request.GET.get('category')      
    categories = Category.objects.all()
    blogs = BlogPost.objects.all().order_by('-created_on')
    blogscount = blogs.count()

    if selected_category:
        blogs = blogs.filter(category__id=selected_category)

    paginator = Paginator(blogs, 6)          # 6 posts per page — change this number as you like
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    trending_post = (
        BlogPost.objects
        .annotate(like_count=Count('reactions', filter=Q(reactions__reaction_type='like')))
        .order_by('-like_count', '-created_on')
        .first()
    )

    context = {
        'blogs':page_obj,
        'blogscount':blogscount,
        'categories': categories,
        'selected_category': selected_category,
    }
    return render(request,'posts/home.html',context)


@login_required
def blogposts(request):
    selected_category = request.GET.get('category')
    categories = Category.objects.all()
    blogs = BlogPost.objects.filter(created_by=request.user).order_by('-created_on')
    blogscount = blogs.count()

    if selected_category:
        blogs = blogs.filter(category__id=selected_category)

    paginator = Paginator(blogs, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'blogs':page_obj,
        'blogscount':blogscount,
        'categories': categories,
        'selected_category': selected_category,

    }
    return render(request,'posts/blogposts.html',context)

@login_required
def create(request):
    form = BlogForm()

    today_post_count = BlogPost.objects.filter(
        created_by=request.user,
        created_on__date=timezone.now().date()
    ).count()

    DAILY_POST_LIMIT = 10

    if request.method == "POST":
        if today_post_count >= DAILY_POST_LIMIT:
            messages.error(
                request,
                f"You've reached your limit of {DAILY_POST_LIMIT} posts for today. Try again tomorrow."
            )
            return redirect('create')

        form = BlogForm(request.POST, request.FILES)

        if form.is_valid():
            title = form.cleaned_data['title']
            content = form.cleaned_data['content']
            video = form.cleaned_data['video']
            category = form.cleaned_data['category']
            tags = form.cleaned_data['tags']

            blog = BlogPost(
                title=title,
                content=content,
                video=video,
                category=category,
                created_by=request.user
            )

            blog.save()
            blog.tags.set(tags)

            # Get all selected images
            images = request.FILES.getlist('images')

            # Save each image separately
            for image in images:
                PostImage.objects.create(
                    post=blog,
                    image=image
                )

            return redirect('blogposts')

    remaining_posts = DAILY_POST_LIMIT - today_post_count

    context = {
        'form': form,
        'remaining_posts': remaining_posts,
        'daily_limit': DAILY_POST_LIMIT,
    }

    return render(request, 'posts/create.html', context)

@login_required
def edit(request,pk):
    blog = BlogPost.objects.get(id=pk)

    if request.user != blog.created_by and not request.user.is_superuser:
         return redirect('home')
    

    form = BlogForm(instance=blog)

    if request.method == "POST":
        form = BlogForm(request.POST, request.FILES, instance=blog)
        if form.is_valid():
            form.save()
            return redirect('home')
    context = {'form':form}
    return render(request,'posts/edit.html',context)

@login_required
def delete(request,pk):
        blog = BlogPost.objects.get(id=pk)

        if request.user != blog.created_by and not request.user.is_superuser:
         return redirect('home')

        if request.method =='POST':
            blog.delete()
            return redirect('home')
        context = {'blog':blog}
        return render(request,'posts/delete.html',context)


def details(request, pk):
    blog = get_object_or_404(BlogPost, id=pk)

    blog.views_count += 1
    blog.save(update_fields=['views_count'])

    like_count    = blog.reactions.filter(reaction_type='like').count()
    dislike_count = blog.reactions.filter(reaction_type='dislike').count()

    comments      = Comment.objects.filter(post=blog).order_by('-created_on')
    comment_count = comments.count()

    user_reaction = None
    user_reported = False

    if request.user.is_authenticated:
        try:
            user_reaction = blog.reactions.get(user=request.user).reaction_type
        except Reaction.DoesNotExist:
            pass
        user_reported = blog.reports.filter(user=request.user).exists()

    context = {
        'blog': blog,
        'like_count': like_count,
        'dislike_count': dislike_count,
        'user_reaction': user_reaction,
        'user_reported': user_reported,
        'comments': comments,
        'comment_count': comment_count,
    }
    return render(request, 'posts/details.html', context)



def search(request):
    query = request.GET.get('q', '')
    results = []

    if query:
        results = BlogPost.objects.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query) |
            Q(category__name__icontains=query) |
            Q(tags__name__icontains=query) |
            Q(created_by__username__icontains=query)
        ).distinct().order_by('-created_on')

    context = {
        'query': query,
        'results': results,
    }
    return render(request, 'posts/search_results.html', context)    


@login_required
def react(request, pk):
    """Like or dislike a post. Clicking the same button again removes the reaction."""
    if request.method != 'POST':
        return redirect('details', pk=pk)

    blog = get_object_or_404(BlogPost, id=pk)
    reaction_type = request.POST.get('reaction_type')  # 'like' or 'dislike'

    if reaction_type not in (Reaction.LIKE, Reaction.DISLIKE):
        return redirect('details', pk=pk)

    existing = Reaction.objects.filter(post=blog, user=request.user).first()

    if existing:
        if existing.reaction_type == reaction_type:
            # Same button clicked again → toggle off (remove reaction)
            existing.delete()
        else:
            # Switch like ↔ dislike
            existing.reaction_type = reaction_type
            existing.save()
    else:
        Reaction.objects.create(post=blog, user=request.user, reaction_type=reaction_type)

    return redirect('details', pk=pk)


@login_required
def report_post(request, pk):
    """Report a post. One report per user per post."""
    blog = get_object_or_404(BlogPost, id=pk)

    if request.method == 'POST':
        already_reported = Report.objects.filter(post=blog, user=request.user).exists()
        if not already_reported:
            reason = request.POST.get('reason', Report.OTHER)
            description = request.POST.get('description', '')
            Report.objects.create(
                post=blog,
                user=request.user,
                reason=reason,
                description=description
            )
    return redirect('details', pk=pk)

@login_required
def add_comment(request, pk):
    blog = get_object_or_404(BlogPost, id=pk)
    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        if content:
            Comment.objects.create(
                post=blog,
                user=request.user,
                content=content
            )
    return redirect('details', pk=pk)


# ── NEW: Delete comment ───────────────────────────────────────────────────────

@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)

    if request.user == comment.user or request.user.is_superuser:
        post_id = comment.post.id
        comment.delete()
        return redirect('details', pk=post_id)
    return redirect('home')


@login_required
def manage_users(request):
    if not request.user.is_superuser:
        return redirect('home')

    users = User.objects.all().order_by('-date_joined')
    context = {'users': users}
    return render(request, 'posts/manage_users.html', context)


@login_required
def toggle_user_active(request, user_id):
    if not request.user.is_superuser:
        return redirect('home')

    target_user = get_object_or_404(User, id=user_id)
    if target_user == request.user:
        return redirect('manage_users')

    target_user.is_active = not target_user.is_active
    target_user.save(update_fields=['is_active'])
    return redirect('manage_users')


@login_required
def delete_user(request, user_id):
    if not request.user.is_superuser:
        return redirect('home')

    target_user = get_object_or_404(User, id=user_id)
    if target_user == request.user:
        return redirect('manage_users')

    target_user.delete()
    return redirect('manage_users')


#AI SUMMARIZER------

logger = logging.getLogger(__name__)

@require_POST
def summarize_post(request, post_id):
    post = get_object_or_404(BlogPost, id=post_id)

    # Return cached summary if it already exists — avoids calling the API again
    if post.summary:
        return JsonResponse({"summary": post.summary, "cached": True})

    try:
        summary = generate_summary(post.title, post.content)
        post.summary = summary
        post.save(update_fields=["summary"])
        return JsonResponse({"summary": summary, "cached": False})
    except Exception:
        logger.exception(f"Summarization failed for post {post_id}")
        return JsonResponse(
            {"error": "Could not generate summary right now. Please try again later."},
            status=500
        )
# video controls-----------
import os
from django.conf import settings
from django.http import StreamingHttpResponse, Http404


def stream_video(request, path):
    file_path = os.path.abspath(os.path.join(settings.MEDIA_ROOT, path))

    # Prevent paths outside MEDIA_ROOT
    media_root = os.path.abspath(settings.MEDIA_ROOT)

    if not file_path.startswith(media_root + os.sep):
        raise Http404("Invalid video path")

    if not os.path.isfile(file_path):
        raise Http404("Video not found")

    file_size = os.path.getsize(file_path)

    range_header = request.headers.get("Range")

    # Browser didn't request a specific range
    if not range_header:
        response = StreamingHttpResponse(
            open(file_path, "rb"),
            content_type="video/mp4"
        )

        response["Content-Length"] = file_size
        response["Accept-Ranges"] = "bytes"

        return response

    # Example:
    # Range: bytes=1000000-
    # Range: bytes=1000000-2000000

    try:
        range_value = range_header.strip().replace("bytes=", "")

        start_str, end_str = range_value.split("-", 1)

        # Handle normal range: bytes=100000-
        if start_str:
            start = int(start_str)
        else:
            # Handle suffix range: bytes=-500000
            suffix_length = int(end_str)
            start = max(file_size - suffix_length, 0)

        if end_str and start_str:
            end = int(end_str)
        else:
            end = file_size - 1

        # Validate range
        if start >= file_size or start < 0:
            response = StreamingHttpResponse(status=416)
            response["Content-Range"] = f"bytes */{file_size}"
            return response

        end = min(end, file_size - 1)

        if start > end:
            response = StreamingHttpResponse(status=416)
            response["Content-Range"] = f"bytes */{file_size}"
            return response

        content_length = end - start + 1

        def file_iterator():
            with open(file_path, "rb") as video:
                video.seek(start)

                remaining = content_length

                while remaining > 0:
                    chunk_size = min(64 * 1024, remaining)
                    chunk = video.read(chunk_size)

                    if not chunk:
                        break

                    remaining -= len(chunk)
                    yield chunk

        response = StreamingHttpResponse(
            file_iterator(),
            status=206,
            content_type="video/mp4"
        )

        response["Content-Length"] = content_length
        response["Content-Range"] = f"bytes {start}-{end}/{file_size}"
        response["Accept-Ranges"] = "bytes"

        return response

    except (ValueError, TypeError):
        raise Http404("Invalid video range")