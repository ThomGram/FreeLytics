from string import Template


def template_to_query_substitution(query, substitution_dict):
    template = Template(query)

    return template.substitute(substitution_dict)
