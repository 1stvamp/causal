var messages_wrapper = null;
function add_message(item) {
    var message = $($('#message_template').jqote(item, '*')).hide();
    $(messages_wrapper, "ul.messages-list-" + item.extra_tags).append(message);
    if (!messages_wrapper.hasClass(item.extra_tags)) {
        messages_wrapper.addClass(item.extra_tags);
    }
    if (messages_wrapper.is(':hidden')) {
        messages_wrapper.fadeIn(500);
    }
    message.fadeIn(500);

    setTimeout(function() {
        messages_wrapper.fadeOut(500, function() {
            message.remove();
            messages_wrapper.removeClass(item.extra_tags);
        });
    }, 3000);
}

$(function() {
    $('#messages').ajaxComplete(function(e, xhr, settings) {
	if (xhr && xhr.responseText !== undefined &&
	  (xhr.responseText.charAt(0) == '[' || xhr.responseText.charAt(0) == '{')) {
	    var json = jQuery.parseJSON(xhr.responseText);
	    if (json.django_messages !== undefined) {
	        $.each(json.django_messages, function(i, item){
		    add_message(item);
		});
	    }
	}
    }).ajaxError(function(e, xhr, settings, exception) {
        add_message({
            message: "There was an error processing your request, please try again.",
            extra_tags: "error"
        });
    });
    messages_wrapper = $('#messages');
    if (messages_wrapper.is(':visible')) {
        messages_wrapper.fadeOut(6000);
    }
});
