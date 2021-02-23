import yaml
import argparse
import os
from jinja2 import Environment, FileSystemLoader

def prepare_dict_for_render(reqs_yml, release):
    res = dict()

    # prepare general section
    res['project_name'] = reqs_yml['general']['project_name']
    res['author'] = reqs_yml['general']['author']
    res['description'] = reqs_yml['general']['description']
    res['data'] = reqs_yml
    res['version'] = reqs_yml['general']['history'][-1]['version']

    res['release'] = release

    # key stakeholders
    res['stakeholders'] = []
    for user in reqs_yml['domain']['stakeholders']:
        res['stakeholders'].append(user)

    # store releases order
    releases = dict()
    for idx, rel in enumerate(reqs_yml['releases']):
        releases[rel['name']] = (idx, rel)

    # requirements
    res['reqs'] = []
    if release in releases:
        for feature in reqs_yml['functional_requirements']:
            feature['requirements'] = [
                        r for r in feature['requirements']
                        if r['release'] in releases and releases[r['release']][0] <= releases[release][0]
                    ]
            res['reqs'].append(feature)

    return res

def render(data, template_path, output_path):
    t_path, t_name = os.path.split(template_path)
    file_loader = FileSystemLoader(t_path)
    env = Environment(loader = file_loader)

    # pass some functions
    env.globals["enumerate"] = enumerate

    template = env.get_template(t_name)

    output = template.render(**data)
    f = open(output_path, 'w')
    f.write(output)
    f.close()
    print ("Result saved to ", output_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate document with requirements')
    parser.add_argument(
            '-i', '--input',
            required = True,
            type = str,
            help = 'yaml file path with requirements doc')
    parser.add_argument(
            '-r', '--release',
            # required = True,
            type = str,
            help = 'name or release')
    parser.add_argument(
            '-o', '--output',
            # required = True,
            type = str,
            help = 'result doc file path')
    parser.add_argument(
            '-t', '--template',
            # required = True,
            type = str,
            help = 'template doc file path')

    args = parser.parse_args()
    with open(args.input) as file:
        reqs_yml = yaml.load(file, Loader = yaml.FullLoader)
        render(prepare_dict_for_render(reqs_yml, args.release), args.template, args.output)
