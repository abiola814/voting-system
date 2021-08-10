from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count
from django.contrib import messages
from .models import Poll, Choice, Vote
from django.http import HttpResponse
from .forms import EditPollForm, ChoiceAddForm



@login_required()
def polls_add(request):
    if request.user.has_perm('votes.add_poll'):
        if request.method == 'POST':
            normination = request.POST.get('norminate')
            normination2 = request.POST.get('norminate2')
            normination3 = request.POST.get('norminate3')
            normination4 = request.POST.get('norminate4')
            polls = request.POST.get('poll')
            poll = Poll(owner = request.user, text= polls)
            poll.save()
            new_choice1 = Choice(
                poll=poll, choice_text= normination).save()
            new_choice2 = Choice(
                poll=poll, choice_text= normination2).save()
            new_choice3 = Choice(
                poll=poll, choice_text= normination3).save()
            new_choice4 = Choice(
                poll=poll, choice_text= normination4).save()
            
            messages.success(
                request, "categories & normination added successfully", extra_tags='alert alert-success alert-dismissible fade show')

            return redirect('vote:add')
        else:
            pass
        return render(request, 'addcart.html')
    else: 
        return HttpResponse("Sorry but you don't have permission to do that!")

@login_required
def polls_edit(request, poll_id):
    poll = get_object_or_404(Poll, pk=poll_id)
    if request.user != poll.owner:
        return redirect('home')

    if request.method == 'POST':
        form = EditPollForm(request.POST, instance=poll)
        if form.is_valid:
            form.save()
            messages.success(request, "Poll Updated successfully",
                             extra_tags='alert alert-success alert-dismissible fade show')
            return redirect("vote:list")

    else:
        form = EditPollForm(instance=poll)

    return render(request, "editcart.html", {'form': form, 'poll': poll})

@login_required
def polls_delete(request, poll_id):
    poll = get_object_or_404(Poll, pk=poll_id)
    if request.user != poll.owner:
        return redirect('home')
    poll.delete()
    messages.success(request, "Poll Deleted successfully",
                     extra_tags='alert alert-success alert-dismissible fade show')
    return redirect("vote:list")


@login_required()
def polls_list(request):
    all_polls = Poll.objects.all()
    search_term = ''

    if 'search' in request.GET:
        search_term = request.GET['search']
        all_polls = all_polls.filter(text__icontains=search_term)

    paginator = Paginator(all_polls, 40)  # Show 6 contacts per page
    page = request.GET.get('page')
    polls = paginator.get_page(page)

    get_dict_copy = request.GET.copy()
    params = get_dict_copy.pop('page', True) and get_dict_copy.urlencode()
    print(params)
    context = {
        'polls': polls,
        'params': params,
        'search_term': search_term,
    }
    return render(request, 'votelist.html', context)



def poll_detail(request, poll_id):
    poll = get_object_or_404(Poll, id=poll_id)
    

    if not poll.active:
        messages.error(
            request, "voting has been closed", extra_tags='alert alert-warning alert-dismissible fade show')
        return redirect("vote:list")
    loop_count = poll.choice_set.count()
    context = {
        'poll': poll,
        'loop_time': range(0, loop_count),
    }
    return render(request, 'choice.html', context)

def result(request):
    polls = Poll.objects.all()
    info = 'result'
    return render(request, 'result.html', {'polls': polls,'info': info})

@login_required
def add_choice(request, poll_id):
    poll = get_object_or_404(Poll, pk=poll_id)
    if request.user != poll.owner:
        return redirect('home')

    if request.method == 'POST':
        form = ChoiceAddForm(request.POST)
        if form.is_valid:
            new_choice = form.save(commit=False)
            new_choice.poll = poll
            new_choice.save()
            messages.success(
                request, "Choice added successfully", extra_tags='alert alert-success alert-dismissible fade show')
            return redirect('vote:edit', poll.id)
    else:
        form = ChoiceAddForm()
    context = {
        'form': form,
    }
    return render(request, 'add_choice.html', context)


@login_required
def choice_edit(request, choice_id):
    choice = get_object_or_404(Choice, pk=choice_id)
    poll = get_object_or_404(Poll, pk=choice.poll.id)
    if request.user != poll.owner:
        return redirect('home')

    if request.method == 'POST':
        form = ChoiceAddForm(request.POST, instance=choice)
        if form.is_valid:
            new_choice = form.save(commit=False)
            new_choice.poll = poll
            new_choice.save()
            messages.success(
                request, "Choice Updated successfully", extra_tags='alert alert-success alert-dismissible fade show')
            return redirect('vote:edit', poll.id)
    else:
        form = ChoiceAddForm(instance=choice)
    context = {
        'form': form,
        'edit_choice': True,
        'choice': choice,
    }
    return render(request, 'add_choice.html', context)


@login_required
def choice_delete(request, choice_id):
    choice = get_object_or_404(Choice, pk=choice_id)
    poll = get_object_or_404(Poll, pk=choice.poll.id)
    if request.user != poll.owner:
        return redirect('home')
    choice.delete()
    messages.success(
        request, "Choice Deleted successfully", extra_tags='alert alert-success alert-dismissible fade show')
    return redirect('vote:edit', poll.id)

@login_required
def poll_vote(request, poll_id):
    poll = get_object_or_404(Poll, pk=poll_id)
    choice_id = request.POST.get('choice')
    if not poll.active:
        messages.error(
            request, "voting has been closed", extra_tags='alert alert-warning alert-dismissible fade show')
        return redirect("vote:list")   
    if not poll.user_can_vote(request.user):
        messages.error(
            request, "You already voted this category", extra_tags='alert alert-warning alert-dismissible fade show')
        return redirect("vote:list")

    if choice_id:
        choice = Choice.objects.get(id=choice_id)
        vote = Vote(user=request.user, poll=poll, choice=choice)
        vote.save()
        print(vote)
        messages.error(request, "You have succesfully voted", extra_tags='alert alert-warning alert-dismissible fade show')
        return redirect("vote:list")
    else:
        messages.error(
            request, "No choice selected", extra_tags='alert alert-warning alert-dismissible fade show')
        return redirect("vote:detail", poll_id)
    return render(request, 'votelist.html', {'poll': poll})

@login_required
def endpoll(request):
    all_polls = Poll.objects.all()
    for poll in all_polls:
        if poll.active is True:
            poll.active = False
            poll.save()
            return redirect("vote:list")
    else:
        return redirect("vote:list")
