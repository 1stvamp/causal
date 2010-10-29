/*
Example usage:

<div>
    <ul id="causal-widget-list"></ul>
</div>
<script type="text/javascript" src="http://blah/static/js/widget.js"></script>
<script type="text/javascript">
// <![CDATA[
var widget = new CausalWidget();
widget.username = 'wes';
// ]]>
</script>
*/

// Placeholder callback, should be set to the actual callback in CausalWidget
var causal_widget_callback = function(data) {}

function CausalWidget() {
    self = this;
    this.stack = [];
    this.interval = null;
    this.loaded = null; // has DOMContentLoaded or window.onload fired
    this.widget = null;
    this.site_base = 'http://localhost:8000';
    this.username = 'test';
    
    // Force one poll immediately when the document DOMContentLoaded event fires.
    // This may be sooner than the next schedualed poll.
    // Can't add this listener in at least Firefox 2 through DOM0 property assignment.
    if (document.addEventListener) {
        document.addEventListener('DOMContentLoaded', this.lastPoll, false);
    } else if (document.attachEvent) {
        // optimistic that one day Internet Explorer will support this event
        document.attachEvent('onDOMContentLoaded', this.lastPoll);
    }
    
    // Force one poll immediately when window.onload fires. For some pages if
    // the brower doesn't support DOMContentLoaded the window.onload event
    // may be sooner than the next schedualed poll.
    window.onload = this.lastPoll;
    
    causal_widget_callback = this.widget_callback;
    
    this.onContentAvailable('causal-widget-list', function(){
        self.widget = document.getElementById('causal-widget-list');
        self.widget.className = self.widget.className + ' causal-widget-loaded';
        var data_script = document.createElement('script');
        data_script.type = 'text/javascript';
        data_script.src = self.site_base + '/' + self.username + '/widget.json?callback=causal_widget_callback';
        self.widget.appendChild(data_script);
    });
}

// does the element or one of it's ancestors have a nextSibling?
CausalWidget.prototype.hasNextSibling = function(el) {
    return el.nextSibling ||
        (el.parentNode && this.hasNextSibling(el.parentNode));
}

CausalWidget.prototype.doPoll = function() {
    var notFound = [];
    for (var i=0; i < this.stack.length; i++) {
        var el = document.getElementById(this.stack[i].id);

        if (el && (this.hasNextSibling(el) || this.loaded)) {
            this.stack[i].callback();
        } else {
            notFound.push(this.stack[i]);
        }
    }
    this.stack = notFound;
    if (notFound.length < 1 || this.loaded) {
        this.stopPolling();
    }
}

CausalWidget.prototype.startPolling = function() {
    if (this.interval) {
        return;
    }
    this.interval = setInterval(this.doPoll, 10);
}

CausalWidget.prototype.stopPolling = function() {
    if (!this.interval) {
        return;
    }
    clearInterval(this.interval);
    this.interval = null;
}

CausalWidget.prototype.onContentAvailable = function(id, callback) {
    this.stack.push({id: id, callback: callback});  
    this.startPolling();
}

CausalWidget.prototype.lastPoll = function() {
    if (this.loaded) {
        return;
    }
    this.loaded = true;
    this.doPoll();
}

CausalWidget.prototype.widget_callback = function(data) {
    settimeout(500, function(){
        var item = data.pop();
        list_item = document.createElement('li');
        list_item.className = item.class;
        list_item.innerHTML = item.date + ': ' + item.body;
        this.widget.appendChild(list_item);
    });
}