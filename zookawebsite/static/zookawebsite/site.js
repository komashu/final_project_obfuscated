/* This is used to enable CSRF protection with Django */
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
var csrftoken = getCookie('csrftoken');

/* Code to execute when DOM is ready. See also https://api.jquery.com/ready/.*/
$(function() {
    /* ---------- Disable moving to top on Site Website ---------- */
    $('a[href="#"][data-top!=true]').click(function(e) {
        e.preventDefault();
    });

    /*------- Site Search ---------*/
    var searchSource;
    $('#globalSearch').typeahead({
        source: function(query, process) {
            if (searchSource === undefined) {
                //Initial load
                return $.ajax({
                    url: '/search',
                    type: 'POST',
                    beforeSend: function(xhr, settings) {
                        if (!(/^(GET|HEAD|OPTIONS|TRACE)$/.test(settings.type)) && !this.crossDomain) {
                            xhr.setRequestHeader("X-CSRFToken", csrftoken);
                        }
                    }
                }).done(function(data) {
                    searchSource = data;
                    return process(searchSource["names"]);
                });
            } else {
                process(searchSource["names"]);
            }
        },
        updater: function(name) {
            window.open("/" + searchSource.uriLookup[name].uri, "_self");
            return name;
        },
        highlighter: function(item) {
            //Highlight Bold Search Text
            var query = this.query.replace(/[\-\[\]{}()*+?.,\\\^$|#\s]/g, '\\$&');
            var title = item.replace(new RegExp('(' + query + ')', 'ig'), function($1, match) {
                return '<strong>' + match + '</strong>';
            });

            //Add alias text
            var html = "<div>" + title + "</div>";
            if (searchSource.uriLookup[item].foundOn) {
                html += "<small>Found on the " + searchSource.uriLookup[item].foundOn + " page</small>";
            }
            return html;
        }
    });
});
