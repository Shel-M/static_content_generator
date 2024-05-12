import os
import shutil
from htmlnode import ParentNode


def copy_recursive(path, target):
    if not os.path.exists(target):
        print(f"creating target {target} directory")
        os.mkdir(target)

    if not os.path.exists(path):
        raise Exception(f"{path} does not exist")

    for file in os.listdir(path):
        filepath = os.path.join(path, file)
        filetarget = os.path.join(target, file)

        if os.path.isfile(filepath):
            shutil.copy(filepath, filetarget)
        else:
            copy_recursive(filepath, filetarget)


def generate_page(from_path, template_path, target_path):
    md_file = open(from_path)

    md_file = md_file.read()
    html_content = ParentNode.from_markdown(md_file)
    html_title = html_content.extract_title()

    template = open(template_path).read()
    template_result = template.replace("{{ Title }}", html_title)
    template_result = template_result.replace(
        "{{ Content }}", html_content.to_html())

    target_file = open(target_path, "w+")
    target_file.write(template_result)


def generate_recursive(from_path, template_path, target_path):
    if not os.path.exists(target_path):
        print(f"creating target {target_path} directory")
        os.mkdir(target_path)

    if not os.path.exists(from_path):
        raise Exception(f"{from_path} does not exist")

    for file in os.listdir(from_path):
        filepath = os.path.join(from_path, file)
        filetarget = os.path.join(target_path, file)

        if os.path.isfile(filepath):
            if filetarget.endswith(".md"):
                filetarget = filetarget.rstrip(".md") + ".html"
            print(f"Generating {filepath} at {filetarget}")
            generate_page(filepath, template_path, filetarget)
        else:
            generate_recursive(filepath, template_path, filetarget)


def main():
    static_path = "./static"
    content_path = "./content"
    template_path = "template.html"
    target_path = "./public"

    shutil.rmtree(target_path)
    copy_recursive(static_path, target_path)

    generate_recursive(content_path, template_path, target_path)


if __name__ == "__main__":
    main()
