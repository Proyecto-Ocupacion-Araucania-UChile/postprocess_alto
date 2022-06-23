import click

from src.opt.click import RequiredOption

@click.command()
@click.option("-t", "--text", "text", is_flag=True, show_default=True, default=False, help="Text generation to do list \
                frequency of data ground truth. Option [frequency] is required !")
@click.option("-f", "--frequency", "frequency", is_flag=True, show_default=True, default=False, cls=RequiredOption,
              required_if="text", help="To do list of world frequency of data ground truth")
@click.option("-m", "--manual", "manual", is_flag=True, show_default=True, default=False, cls=RequiredOption, required_if=["security", "image"], )
@click.option("-i", "--image", "image", is_flag=True, show_default=True, default=False, help="To appear jpg associated in folder \"img\". Option [manual] is required !")
@click.option("-s", "--security", "security", is_flag=True, show_default=True, default=False, help="Security mode to execute the change. Option [manual] is required !")

def corrector(frequency, text, manual, image, security):
    return

if __name__ == '__main__':
    corrector()