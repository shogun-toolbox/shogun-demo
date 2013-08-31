{% for panel in panels %}
  {% if panel.panel_name == 'arguments' %}
    {% for argument in panel.panel_property %}
      {% if argument.argument_type == 'button-group' %}
        {% for button in argument.argument_items %}
          {% if button.button_type == 'json_up_down_load' %}
          function {{ button.button_name }}_action()
          {
              var request_data = {
                  csrfmiddlewaretoken: '{{ csrf_token }}',
                  point_set: JSON.stringify(point_set),
                  axis_domain: JSON.stringify({'horizontal': x.domain(),
                                               'vertical': y.domain()}),
                  {% for panel in panels %}
                    {% if panel.panel_name == 'arguments' %}
                      {% for argument in panel.panel_property %}
                        {% if argument.argument_name %}
                          '{{ argument.argument_name }}': document.arguments.{{ argument.argument_name }}.value,
                        {% endif %}
                      {% endfor %}
                  {% endif %}{% endfor %}
              };
    
              $.ajax(
                  {
                      url: '{{ button.button_name }}',
                      type: 'POST',
                      dataType: "text",
                      data: request_data,
                      beforeSend: function(){$("#{{ button.button_name }}").attr('disabled', true);},
                      success: {{ button.button_name }},
                      error: function(){alert("Error!");$("#{{ button.button_name }}").attr('disabled', false);},
                  }); 
          }
          {% endif %}
        {% endfor %}
      {% endif %}
    {% endfor %}
  {% endif %}
{% endfor %}
