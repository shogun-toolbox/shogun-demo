{% for panel in panels %}
  {% if panel.panel_name == 'arguments' %}
    {% for argument in panel.panel_property %}
      {% if argument.argument_type == 'button-group' %}
        {% for button in argument.argument_items %}
          {% if button.button_type == 'json_up_down_load' %}
          function {{ button.button_name }}_action()
          {
              request_data = {
                  csrfmiddlewaretoken: '{{ csrf_token }}',
                  {% if template.mouse_click_enabled == 'both' or template.mouse_click_enabled == 'left' %}
                  mouse_left_click_point_set: JSON.stringify(mouse_left_click_point_set),
                  {% if template.mouse_click_enabled == 'both' %}
                  mouse_right_click_point_set: JSON.stringify(mouse_right_click_point_set),
                  {% endif %}
                  {% endif %}
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
