import re
import typer
import os

from jinja2 import Environment, PackageLoader, select_autoescape

env = Environment(
    loader=PackageLoader("app", package_path="codegen"),
    autoescape=select_autoescape()
)


def camel_to_snake(name):
    name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', name).lower()


def pluralize(noun):
    if re.search('[sxz]$', noun):
        return re.sub('$', 'es', noun)
    elif re.search('[^aeioudgkprt]h$', noun):
        return re.sub('$', 'es', noun)
    elif re.search('[aeiouy]$', noun):
        return re.sub('y$', 'ies', noun)
    else:
        return noun + 's'


def save_to_file(content, file_name):
    with open(file_name, "w") as f:
        f.write(content)


def get_file(file_name):
    if not os.path.isfile(file_name):
        print(f"File {file_name} does not exist!")
        exit(1)

    with open(file_name) as f:
        content = f.read()
    return content


def parse_model(model_name):
    model_file = get_file(f"models/{camel_to_snake(model_name)}.py")
    type_mapping = {'String': 'str', 'Integer': 'int', 'Date': 'datetime.date',
                    'Float': 'float', 'Boolean': 'bool', 'JSON': 'list'}
    fields = re.findall("(\w+) = Column\((\w+), (nullable|default)=(\w+)\)", model_file)  # noqa
    schema_fields = {}
    for field in fields:
        default = 'None'
        set_default = False
        if field[2] == 'default':
            default = field[3]
            set_default = True

        if field[2] == 'nullable' and field[3] == 'False':
            if set_default:
                new_field = f'{field[0]}: {type_mapping[field[1]]} = {default}'
            else:
                new_field = f'{field[0]}: {type_mapping[field[1]]}'
        else:
            new_field = f'{field[0]}: Optional[{type_mapping[field[1]]}] = {default}'

        schema_fields.setdefault(field[0], new_field)

    relations = re.findall('(\w+) = relationship\("(\w+)", (back_populates|backref)="(\w+)"\)', model_file)  # noqa
    related_fields = {}
    for field in relations:
        related_fields.setdefault(field[0], {'related_model': field[1], 'back_populates': field[2]})
    return schema_fields, related_fields


def generate_schema(model_name, schema_fields, related_fields):
    schema_template = env.get_template("schemas_entity.py.tpl")
    save_to_file(schema_template.render(entity=model_name, schema_fields=schema_fields, related_fields=related_fields),
                 f'codegen/generated/schemas_{camel_to_snake(model_name)}.py')


def install_files(model_name):
    pn = camel_to_snake(pluralize(model_name))

    api_file_path = "api/api_v1/api.py"
    api_file = get_file(api_file_path)
    if pn not in api_file:
        api_file = re.sub("(endpoints\simport[\w\s,]+)\n\n", f"\g<1>, {pn}\n\n", api_file) # noqa
        new_route = 'api_router.include_router(' + pn + '.router, prefix="/' + pn + '", tags=["' + pn + '"])'
        save_to_file(api_file.strip() + "\n" + new_route + "\n", api_file_path)
    else:
        print("No need update api.py")

    os.rename(f"codegen/generated/endpoints_{camel_to_snake(model_name)}.py", f"api/api_v1/endpoints/{pn}.py")
    os.rename(f"codegen/generated/crud_{camel_to_snake(model_name)}.py", f"crud/crud_{camel_to_snake(model_name)}.py")
    os.rename(f"codegen/generated/schemas_{camel_to_snake(model_name)}.py", f"schemas/{camel_to_snake(model_name)}.py")

    crud_init_file_path = 'crud/__init__.py'
    crud_init = get_file(crud_init_file_path)

    if camel_to_snake(model_name) not in crud_init:
        new_crud = f"from .crud_{camel_to_snake(model_name)} import {camel_to_snake(model_name)}"
        save_to_file(crud_init.strip() + '\n' + new_crud + '\n', crud_init_file_path)
    else:
        print("No need update crud/__init__.py")

    schemas_init_file_path = 'schemas/__init__.py'
    schemas_init = get_file(schemas_init_file_path)

    if camel_to_snake(model_name) not in schemas_init:
        new_schemas = f"from .{camel_to_snake(model_name)} import {model_name}, " \
                      f"{model_name}Create, {model_name}InDB, {model_name}Update"
        save_to_file(schemas_init.strip() + '\n' + new_schemas + '\n', schemas_init_file_path)
    else:
        print("No need update schemas/__init__.py")


def main(model_name: str):
    if model_name is None:
        model_name = typer.prompt("Please enter model name (Model)?")
    schema_fields, related_fields = parse_model(model_name)

    if not os.path.isdir('codegen/generated'):
        os.mkdir('codegen/generated')

    generate_schema(model_name, schema_fields, related_fields)
    pn = camel_to_snake(pluralize(model_name))
    if "owner" in related_fields:
        crud_template = env.get_template("crud_entity_with_owner.py.tpl")
    else:
        crud_template = env.get_template("crud_entity.py.tpl")
    save_to_file(crud_template.render(entity=model_name, entity_lower=camel_to_snake(model_name), pn=pn),
                 f'codegen/generated/crud_{camel_to_snake(model_name)}.py')
    if "owner" in related_fields:
        endpoints_template = env.get_template("endpoints_entity_with_owner.py.tpl")
    else:
        endpoints_template = env.get_template("endpoints_entity.py.tpl")
    save_to_file(endpoints_template.render(entity=model_name, entity_lower=camel_to_snake(model_name), pn=pn),
                 f'codegen/generated/endpoints_{camel_to_snake(model_name)}.py')
    is_install = typer.confirm('Install new files?')

    if is_install:
        install_files(model_name)


if __name__ == "__main__":
    typer.run(main)
