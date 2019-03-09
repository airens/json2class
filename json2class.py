import json
from collections import OrderedDict


class ParsedClass:
    def __init__(self, name: str, vars: dict = {}):
        self.name = name
        self.vars = vars

    def update(self, vars):
        self.vars.update(vars)

    def __str__(self):
        init_text = f"    def __init__(self, data: dict):\n"
        repr_text = f'    def __repr__(self):\n        return f"""{self.name}'
        if not self.vars:
            init_text += "pass\n"
        else:
            for key, value in self.vars.items():
                var_name = key.replace('-', '_')
                if type(value) == dict:  # new_class
                    init_text += f'        self.{var_name} = {self.name + make_name(key)}(data.get("{key}", {{}}))\n'
                elif type(value) == list:
                    if value:
                        t = type(value[0])
                        if t == dict or t == list:
                            init_text += f"        self.{var_name} = []\n"
                            init_text += f'        for item in data.get("{key}", []):\n'
                            init_text += f'            self.{var_name}.append({self.name + make_name(key)}(item))\n'
                        else:
                            init_text += f'        self.{var_name} = data.get("{key}")\n'
                else:
                    comment = f" {value}" if value else ""
                    init_text += f'        self.{var_name} = data.get("{key}")  #{comment}\n'
                if type(value) == dict:
                    repr_text += f'\n        {var_name} = {self.name + make_name(key)}()'
                elif type(value) == list:
                    repr_text += f'\n        {var_name} = [] ({{len(self.{key})}} items)'
                else:
                    repr_text += f'\n        {var_name} = {{self.{var_name}}}'
        repr_text += '\n        """\n'
        return f"class {self.name}:\n" + init_text + '\n' + repr_text


parsed_classes = OrderedDict()


def make_name(name: str):
    return name.title().replace('_', '')


def parse(key, value, class_name=""):
    if type(value) == dict:  # new_class
        name = class_name + make_name(key)
        for item in value.items():
            parse(item[0], item[1], name)
        if name not in parsed_classes:
            parsed_classes[name] = ParsedClass(name, value)
        else:
            parsed_classes[name].update(value)
    elif type(value) == list:
        for item in value:
            parse(key, item, class_name)


def main():
    name = input("Enter name: ")
    with open("input.json") as file:
        data = json.loads(file.read())
    parse(name, data)
    with open("result.py", "w") as file:
        for _, parsed_class in parsed_classes.items():
            file.write("\n\n" + str(parsed_class))
    return 0


if __name__ == '__main__':
    main()
