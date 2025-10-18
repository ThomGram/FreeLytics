{% macro revenu_to_min_max_str(column_name, min_or_max) %}
    {% if column_name %}

        {% if min_or_max == "min" %}
            trim(split_part({{ column_name }}, '-', 1))
        {% elif min_or_max == "max" %}
            trim(split_part({{ column_name }}, '-', 2))
        {% else %}
        null
        {% endif %}
    {% else %}
        null
    {% endif %}
{% endmacro %}


{% macro revenu_to_int(column_name) %}
    {% if column_name %}

        case
            when {{column_name}} like '%k%' then
                try_cast(replace({{column_name}}, 'k', '000') as int)
            when {{column_name}} is not null and {{column_name}} != '' then
                try_cast({{column_name}} as int)
            else null
        end

    {% else %}
        null
    {% endif %}
{% endmacro %}
