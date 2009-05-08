# -*- coding: utf-8 -*-
# 
# In order to use this widget you need:
# 1. download YUI library and put it in 
#    your MEDIA folder (http://developer.yahoo.com/yui/)
# 2. Include necessary js and css imports at your page
#    Check for necessary imports at 'YUI autocomplete' page
#    My imports are visible at test_ajax.html
# 3. Assign a widget to field (with schema and lookup_url parameters)
# 4. Define view to do a data lookup for ajax queries
#
import django.forms as forms
from django.utils.safestring import mark_safe
from django.utils.encoding import force_unicode 

#AUTOCOMPLETE
#    <label for="%s">%s</label>

AC_SNIPPET = """
<span class="ac_container">
    <input %s />
    <span id="%s_container" class="yui-skin-sam"></span>

    <script type="text/javascript">
        // An XHR DataSource
        var acServer_%s = "%s";
        var acSchema_%s = %s;
        var acDataSource_%s = new YAHOO.widget.DS_XHR(acServer_%s, acSchema_%s);
        var acAutoComp_%s = new YAHOO.widget.AutoComplete("%s","%s_container", acDataSource_%s);
        acAutoComp_%s.useIFrame = true;
        acAutoComp_%s.animSpeed = 0;
        %s
        %s
    </script>
</span>
"""

def_format_result = 'acAutoComp_%s.formatResult = %s;'
def_item_select_handler = 'acAutoComp_%s.itemSelectEvent.subscribe(%s);'

class AutoCompleteWidget(forms.widgets.TextInput):
    """ widget autocomplete for text fields
    """
    
    def __init__(self, 
                 schema=None, 
                 lookup_url=None, 
                 format_result_fname='', 
                 item_select_handler_fname='', 
                 label='',
                 *args, **kw):
        super(AutoCompleteWidget, self).__init__(*args, **kw)
        # YUI schema
        self.schema = schema
        # url for YUI XHR Datasource
        self.lookup_url = lookup_url
        # optional name of javascript function that formats results (YUI)
        self.format_result_fname = format_result_fname 
        # optional name of javascript function that handles item select event (YUI)
        self.item_select_handler_fname = item_select_handler_fname
        self.label = label

    def render(self, name, value, attrs=None):
        html_id = attrs.get('id', name)
        html_label = self.label

        # url for YUI XHR Datasource
        lookup_url = self.lookup_url
        # YUI schema
        schema = self.schema
        # optional name of javascript function that handles item select event (YUI)
        item_select_handler_fname = getattr(self, 'item_select_handler_fname', '')
        # optional name of javascript function that formats results (YUI)
        format_result_fname = getattr(self, 'format_result_fname', '')        

        if value is None: value = ''
        final_attrs = self.build_attrs(attrs, type=self.input_type, name=name)
        if value != '': final_attrs['value'] = force_unicode(value) # Only add the 'value' attribute if a value is non-empty.
        final_attrs['class'] = 'autocomplete_widget'

        fr = '' # format result
        sh = '' # select handler
        if self.format_result_fname:
            fr = def_format_result % (html_id, self.format_result_fname)
        if self.item_select_handler_fname:
            sh = def_item_select_handler % (html_id,
                                            self.item_select_handler_fname)

        return mark_safe(AC_SNIPPET % (forms.util.flatatt(final_attrs), html_id, html_id,
                             lookup_url,html_id, schema, html_id, html_id,
                             html_id, html_id, html_id, html_id,
                             html_id,html_id, html_id, fr, sh))
#/AUTOCOMPLETE
