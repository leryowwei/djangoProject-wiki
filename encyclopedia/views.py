from random import randrange
from django.shortcuts import render, redirect
from django import forms
from django.contrib import messages
from django.urls import reverse
from . import util


class SearchForm(forms.Form):
    """Search form class"""
    keyword = forms.CharField(label="Search Encyclopedia")


class ContentForm(forms.Form):
    """Content form class"""
    title = forms.CharField()
    content = forms.CharField(widget=forms.Textarea)


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries(),
        "search_form": SearchForm(),
    })


def get_page(request, title):
    """Convert markdown to html """
    # check if page exists
    if title in util.list_entries():
        # call function to convert md to html
        return render(request, "encyclopedia/result.html", {
            "result_in_html": util.convert_md_to_html(title),
            "title": title,
            "search_form": SearchForm(),
        })
    else:
        return render(request, "encyclopedia/page_not_found.html", {
            "title": title,
            "search_form": SearchForm(),
        })


def create_page(request):
    """Create new page"""
    if request.method == "POST":
        # Take in the data the user submitted and save it as form
        form = ContentForm(request.POST)

        # Check if form data is valid (server-side)
        if form.is_valid():
            title = form.cleaned_data['title']
            content = form.cleaned_data['content']

            # only save data if it does not exist in database
            # otherwise, return the same form and an error message
            # take into account of casings
            if title.lower() in util.make_list_lower_case(util.list_entries()):
                messages.error(request, "Error: '{}' already exists in database! Unable to save the entry.".format(title))
                return render(request, "encyclopedia/create.html", {
                    "create_form": form,
                    "search_form": SearchForm(),
                })
            else:
                # save entry
                util.save_entry(title, content)

                # return new page
                return redirect(reverse('get_page', kwargs={'title': title}))
        else:
            return render(request, "encyclopedia/create.html", {
                "create_form": form,
                "search_form": SearchForm(),
            })

    return render(request, "encyclopedia/create.html", {
        "create_form": ContentForm(),
        "search_form": SearchForm(),
    })


def edit_page(request, title):
    """Edit page"""
    if request.method == "POST":
        # Take in the data the user submitted and save it as form
        form = ContentForm(request.POST)

        # Check if form data is valid (server-side)
        if form.is_valid():
            content = form.cleaned_data['content']

            # save entry
            util.save_entry(title, content)

            # return page
            return redirect(reverse('get_page', kwargs={'title': title}))

    form = ContentForm({"title": title, "content": util.get_entry(title)})

    return render(request, "encyclopedia/edit.html", {
        "title": title,
        "edit_form": form,
        "search_form": SearchForm(),
    })


def get_random_page(request):
    """Randomly show a page of info"""
    # get all entries availables
    entries = util.list_entries()

    # use random generator to get the number and then get the title
    rand_num = randrange(0, len(entries), 1)
    title = entries[rand_num]

    return redirect(reverse('get_page', kwargs={'title': title}))


def search_results(request):
    if request.method == "POST":
        form = SearchForm(request.POST)

        # Check if form data is valid (server-side)
        # if fail just tell user no result is found for the keyword they used
        if form.is_valid():
            # get all entries
            entries = util.list_entries()

            # work with lower case
            keyword = form.cleaned_data['keyword'].lower()
            lower_entries = util.make_list_lower_case(entries)

            results = []

            # as long as the word exists then add it to the results list to return back
            for count, entry in enumerate(lower_entries):
                if keyword in entry:
                    results.append(entries[count])

            # if results list got one item and the keyword matches the item name exactly, directly return the page of the result
            if len(results) == 1 and keyword in lower_entries:
                # call function to convert md to html
                return render(request, "encyclopedia/result.html", {
                    "result_in_html": util.convert_md_to_html(keyword),
                    "title": entries[lower_entries.index(keyword)],
                    "search_form": SearchForm(),
                })
            else:
                return render(request, "encyclopedia/search.html", {
                    "results": results,
                    "search_form": SearchForm(),
                })
        else:
            return render(request, "encyclopedia/search.html", {
                "results": [],
                "search_form": SearchForm(),
            })


