# WHAT TO DO:
# >> Add this file to testapp/scripts/pariksha.py
# >> Add a dummy settings.py file with relevant variables ##DONE
# >> Add a dummy urls.py file with relevant variables ##DONE
# >> Write a context manager for directory creation and change ##DONE
# >> Add argparse with relevant arguments
# >> Create seperate command for start_code_server in setup.py
# >> Fix django.db.utils.IntegrityError - by updating initial_fixtures.json

import subprocess
from django.core import management
import contextlib
import os
from os import path
import argparse

###
from django.template import Template, Context, loader
from django.conf import settings
# from django.conf.urls import patterns, include, url


CUR_DIR = os.getcwd()
SCRIPT_DIR = os.path.abspath(os.path.dirname(__file__))
PARENT_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, os.pardir))
TEMPLATE_DIR = path.join(PARENT_DIR, 'templates')

def main():
    #Parse command-line to obtain the arguments and/or options
    msg = ("Enter the subcommand to be executed.\n"
    "Available subcommands:\n"
    "create_demo <projectname> [destination-path]\n"
    "run_vimarsh_server")

    parser = argparse.ArgumentParser(prog="vimarsh", 
                                        usage="vimarsh.py subcommand [args]",
                                        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("subcommand", 
                            type=str, 
                            nargs='+', 
                            help=msg)   
    args = parser.parse_args()

    if args.subcommand[0] == "create_demo":
        if len(args.subcommand) > 3 or len(args.subcommand) <= 1:
            parser.print_help()
        elif len(args.subcommand) == 3:
            project_name = args.subcommand[1]
            create_demo(args.subcommand[1], args.subcommand[2])
        else:
            project_name = args.subcommand[1]
            create_demo(args.subcommand[1])

    if args.subcommand[0] == "run_vimarsh_server":
        if len(args.subcommand) > 1 or len(args.subcommand) < 1:
            parser.print_help()
        else:
            try:
                run_vimarsh_server(project_name)
            except UnboundLocalError:
                print "Error: Create a demo with vimarsh.py create_demo <project_name>"
            else:
                parser.print_help()

    else:
        parser.print_help()

    # parser.add_argument("query", 
    #                         type=str, 
    #                         nargs='+', 
    #                         help="enter the Query to be answered")
    # parser.add_argument("-a", 
    #                         "--assumption", 
    #                         action="store_true", 
    #                         help="display the assumptions made (if any) in case of ambiguity")
    # parser.add_argument("-v", 
    #                         "--version", 
    #                         action="version", 
    #                         version="AskIt-Wolfram Alpha version 0.1")
    # args = parser.parse_args()
    # query = "+".join(args.query)
    # if (args.assumption):
    #     assum = 1
    # else:
    #     assum = 0
    
    # askit_getans(query, assum, wolfram_API_ID)

def create_demo(project_name, project_dir=None):
    template_dir = ('.',)

    try:
        management.call_command('startproject', project_name, project_dir)
    # os._chdir() ##context man
    except:
        print "Exiting Vimarsh Installer"

    if project_dir is None:
        top_dir = path.join(os.getcwd(), project_name)
    else:
        top_dir = project_dir # os.path.abspath(path.expanduser(project_dir))

    project_path = path.join(top_dir, project_name)

    with _chdir(top_dir):
        ###
        # AS seen on:
        # http://stackoverflow.com/questions/98135
        # /how-do-i-use-django-templates-without-the-rest-of-django
        ###
        # settings.configure()
        # t = get_template('test.html') 
        # t = Template('My name is {{ my_name }}.')
        # c = Context({'my_name': 'Daryl Spitzer'})
        # t.render(c)

        # custom_apps = ('testapp.exam', 'taggit', 'taggit_autocomplete_modified',)
        # urlpatterns = patterns('', url(r'^exam/', include('testapp.exam.urls')),
        #                             url(r'^taggit_autocomplete_modified/',
        #                             include('taggit_autocomplete_modified.urls')),)
        root_urlconf = "{0}.{1}".format(project_name, 'demo_urls')# path.join(project_path, 'demo_urls.py') ### need to change later

        # if not settings.configured:
        # settings.configure(TEMPLATE_DIRS=(TEMPLATE_DIR,))
        # t1 = loader.get_template('demo_settings.py') 
        # c1 = Context({'project_name': project_name, # 'custom_apps': custom_apps, 
        #                 'root_urlconf': root_urlconf})
        # t1.render(c1)

        # settings.configure(TEMPLATE_DIRS=(TEMPLATE_DIR,)) 
        # t2 = loader.get_template('demo_urls.py') 
        # c2 = Context({'urlpatterns': urlpatterns})
        # t2.render(c2)

        # settings = open('my_demo/settings.py', 'a')
        # settings.write("INSTALLED_APPS += ('testapp.exam', 'taggit', 'taggit_autocomplete_modified', )")
        # settings.close()

        # urls = open('my_demo/urls.py', 'a')
        # urls.write("urlpatterns = patterns('', url(r'^exam/', include('testapp.exam.urls')), url(r'^taggit_autocomplete_modified/', include('taggit_autocomplete_modified.urls')), )")
        # urls.close()

        settings_template_path = path.join(TEMPLATE_DIR, 'demo_settings.py')
        settings_target_path = path.join(project_path, 'demo_settings.py')
        settings_context = Context({'project_name': project_name, # 'custom_apps': custom_apps, 
                        'root_urlconf': root_urlconf})
        urls_template_path = path.join(TEMPLATE_DIR, 'demo_urls.py')
        urls_target_path = path.join(project_path, 'demo_urls.py')
        command = ("python ./manage.py syncdb "
                        "--noinput --settings={0}.demo_settings").format(project_name)

        # Create demo_settings file
        _render_demo_files(settings_template_path, settings_target_path, settings_context)
        # Create demo_urls file 
        _render_demo_files(urls_template_path, urls_target_path)

        subprocess.call(command, shell=True)

def run_vimarsh_server(project_name):
    command = ("python manage.py runserver "
                    "--settings={0}.demo_settings").format(project_name)
    subprocess.call(command, shell=True)

def _render_demo_files(template_path, output_path, context=None):
    with open(template_path, 'r') as template_file:
        content = template_file.read()
        if context:
            content = content.decode('utf-8')
            template = Template(content)
            content = template.render(context)
            content = content.encode('utf-8')

    with open(output_path, 'w') as new_file:
        new_file.write(content)

@contextlib.contextmanager
def _chdir(path):
    starting_directory = os.getcwd()
    try:
        os.chdir(path)
        yield
    finally:
        os.chdir(starting_directory)

if __name__ == '__main__':
    main()
    # create_demo('takerr', '/home/arj/arj_project/imp_dump/test_installer')
