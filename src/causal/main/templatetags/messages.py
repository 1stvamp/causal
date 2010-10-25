from django import template
register = template.Library()

class MessagesNode(template.Node):
    """ Outputs grouped Django Messages Framework messages in separate
        lists sorted by level. """

    def __init__(self, messages):
        self.messages = messages

    def render(self, context):
        try:
            messages = context[self.messages]

            # Make a dictionary of messages grouped by tag, sorted by level.
            grouped = {}
            for m in messages:
                # Add message
                if (m.level, m.tags) in grouped:
                    grouped[(m.level, m.tags)].append(m.message)
                else:
                    grouped[(m.level, m.tags)] = [m.message]

            # Create a list of messages for each tag.
            out_str = ''
            t = template.loader.get_template('causal/snippets/messages.html')
            for level, tag in sorted(grouped.iterkeys()):
                messages_for_t = [m for m in grouped[(level, tag)]]
                out_str += t.render(template.Context({'tag': tag, 'messages': messages_for_t}))
            return out_str

        except KeyError:
            return ''

@register.tag(name='render_messages')
def render_messages(parser, token):
    parts = token.split_contents()
    if len(parts) != 2:
        raise template.TemplateSyntaxError("%r tag requires a single argument"
                                           % token.contents.split()[0])
    return MessagesNode(parts[1])
