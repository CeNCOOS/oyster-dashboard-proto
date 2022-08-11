import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
from dateutil import tz
import itertools
import os
import datetime as dt


def make_figure(num_axes):
    sns.set_context('talk')
    fig, ax = plt.subplots(num_axes,sharex=True,gridspec_kw=dict(hspace=0.2))
    fig.set_size_inches(8, num_axes * 2)
    return fig, ax

def color_maps(num_axes):
    """ Return a list of colors for cycling through """
    palette = itertools.cycle(sns.color_palette())
    return [next(palette) for i in range(num_axes)]

def add_title(super_string, sub_string):
    """Create the title for the plot

    Args:
        super_string (str): _description_
        sub_string (str): _description_
    """
    title = "{}\n{}".format(super_string, sub_string)
    plt.suptitle(title,x=.125,y=.96,horizontalalignment='left',size=20)


def format_axes(ax, short_name, unit, label_color, not_last=True, comments=None):
    
    sns.despine(ax=ax,bottom=True,trim=False);
    ax.yaxis.set_label_position("right")
    ax.yaxis.set_label_coords(1.025,.6)
    label = short_name +  "\n[{}]".format(unit)
    ax.set_ylabel(label, rotation=0, labelpad=0, size=16, color=label_color, fontweight='bold', horizontalalignment='left')
    ax.tick_params(axis='y', labelsize=14)
    ax.spines['left'].set_linewidth(1)
    ax.spines['top'].set_linewidth(1)
    
    if not_last:
        ax.get_xaxis().set_visible(False)
    
    else:
        date_fmt = mdates.DateFormatter('%b %d')
        ax.xaxis.set_major_formatter(date_fmt)
        ax.xaxis.set_minor_locator(mdates.HourLocator(12,tz=tz.gettz('US/Pacific')))
        ax.tick_params(axis='both', labelsize=14)
        ax.get_xaxis().set_visible(True)
        ax.text(-.05,-.65,'Updated on: {}'.format(dt.datetime.now()),transform=ax.transAxes,size=10,c=".75")
    
    if comments is not None:
        ax.text(-.05, -.5, s=comments, transform=ax.transAxes, size=14, c="k")

    return ax


def add_nighttime(ax, sunrise, sunset, stime, etime):
    ax.axvspan(stime, etime, color='.85',zorder=-5)
    for sr,ss in zip(sunrise,sunset):
        ax.axvspan(ss.astimezone(tz=None),sr.astimezone(tz=None), color='w',zorder=-2)
    return ax


def save_fig(fname, directory=".", transfer=False):
    """ Save the figure. The default folder is the current directory

    Args:
        fname (str): string of the filename to save to
        directory (str, optional): provide a path to the location of the file to save. Defaults to ".".
    """
    out_name = os.path.join(directory, fname)
    plt.savefig(out_name, dpi=250, bbox_inches='tight', pad_inches=0.2)
    if transfer:
        copy_file_to_webserver(out_name)


def copy_file_to_webserver(FILE):
    """Copy images from to webserver where they can be viewed publically."""
    try:
        os.system('scp -i /etc/ssh/keys/pdaniel/scp_rsa {} skyrocket8.mbari.org:/var/www/html/data/oyster-dash-proto/ '.format(FILE))
    
    except Exception as e:
        print(e)


def show_fig():
    plt.show()

