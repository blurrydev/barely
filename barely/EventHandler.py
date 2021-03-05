"""
Any actions concerning file translation
have to go through this class. It handles
move/delete events directly, and hands off
new/update events to the ProcessingPipeline
"""

from watchdog.events import FileCreatedEvent, FileModifiedEvent
from watchdog.events import FileDeletedEvent, DirDeletedEvent
from watchdog.events import FileMovedEvent, DirMovedEvent
from binaryornot.check import is_binary
from pathlib import Path
import shutil
import os
import re
from barely.common.config import config
from barely.common.utils import make_valid_path


class EventHandler():
    """ handle events, hand them off, or diregard irrelevant ones """

    def __init__(self):
        pass

    def notify(self, event, full_rebuild=False):
        """ anyone (but usually, the watchdog) can issue a notice of a file event """
        src_dev = event.src_path
        src_web = self._get_web_path(src_dev)

        if self.template_dir in src_dev and not isinstance(event, FileDeletedEvent) and not isinstance(event, DirDeletedEvent) and not full_rebuild:
            if isinstance(event, FileMovedEvent) or isinstance(event, DirMovedEvent):
                src_dev = event.dest_path
            for affected in self._get_affected(src_dev):
                self.notify(FileModifiedEvent(src_path=affected))
        elif "config.yaml" in src_dev or "metadata.yaml" in src_dev:
            # don't do anything. These changes don't have to be tracked.
            pass
        elif re.match(r"\/_[^\/]+\/[^\/]+.{config['PAGE_EXT']}", src_dev):
            parent_page = self._get_parent_page(src_dev)
            self.notify(FileModifiedEvent(src_path=parent_page))
        elif isinstance(event, FileDeletedEvent) or isinstance(event, DirDeletedEvent):
            self._delete(src_web)
        elif isinstance(event, FileMovedEvent) or isinstance(event, DirMovedEvent):
            dest_web = self._get_web_path(event.dest_path)
            self._move(src_web, dest_web)
        elif isinstance(event, FileCreatedEvent) or isinstance(event, FileModifiedEvent):
            type, extension = self._determine_type(src_dev)
            item = {
                "origin": src_dev,
                "destination": src_web,
                "type": type,
                "extension": extension
            }
            self.pipeline.process([item])

            if (extension in ["css", "js", "sass", "scss"] or type == "IMAGE") and not full_rebuild:
                for dependant in self._find_dependants(src_dev):
                    self.notify(FileModifiedEvent(src_path=dependant))
        else:
            pass

    def force_rebuild(self):
        """ rebuild the entire project by first deleting the devroot, then marking every file as new """
        self._delete(config["root"]["web"])
        os.makedirs(config["root"]["web"], exist_ok=True)
        for root, dirs, files in os.walk(config["ROOT"]["DEV"], topdown=False):
            for path in files:
                if self.template_dir not in path:
                    self.notify(FileCreatedEvent(src_path=os.path.join(root, path)), full_rebuild=True)

    def _determine_type(self, path):
        """ determine the type of the file via its extension. return both """
        ext = os.path.splitext(path)[1]
        if ext == config["PAGE_EXT"]:
            return "PAGE", config["PAGE_EXT"]
        elif ext in config["IMAGE_EXT"]:
            return "IMAGE", ext
        elif not is_binary(path):
            return "TEXT", ext
        else:
            return "GENERIC", ext

    def _find_children(self, parent):
        # find all templates. Yes, all of them.
        for path in Path(config["TEMPLATE_DIR"]).rglob("*.html"):
            # open them to check their contents
            with open(path, "r") as file:
                content = file.read()
                matches = re.findall(r'{%\s*extends\s+[\"|\']([^\"]+)[\"|\']\s*%}', content)
                # if an {% extends %} tag is found, this template is potentially affected!
                # check if it extends the one we're looking for.
                # return the children of the child (recursion!)
                # return the child
                if len(matches):
                    if os.path.join(config["TEMPLATE_DIR"], matches[0]) == parent:
                        yield from self._find_children(str(path))
                        yield str(path)

    def _get_affected(self, template):
        """ yield the paths of all files that rely on a certain template """
        # changes can occur on either files or dirs. If it's a dir, all files and subdirs are changed
        changed = []
        if type(template) == list:
            changed = template
        elif os.path.isfile(template):
            changed = [template]
        elif os.path.isdir(template):
            changed = [str(path) for path in Path(template).rglob("*.html")]

        # for every file that was directly changed, find all templates that
        # inherit from it, since these are also in need of a rerender
        affected = changed
        for parent in changed:
            affected.extend(self._find_children(parent))

        # extract the template name, such as it's used in the .md file names
        template_dir_full = os.path.join(config["TEMPLATE_DIR"], "")
        for element in range(len(affected)):
            affected[element] = affected[element].replace(template_dir_full, "")
            affected[element] = affected[element].replace(".html", "")
            affected[element] = affected[element].replace("/", ".")
            affected[element] = affected[element].replace("\\", ".")

        # find all renderable files
        file_candidates = []
        for path in Path(config["ROOT"]["DEV"]).rglob("*" + config["PAGE_EXT"]):
            file_candidates.append(str(path))

        # remove duplicate entries from the lists (prevents multiple re-renders)
        # mostly unnecessary, especially on the file_candidates, but just to be sure...
        affected = list(set(affected))
        file_candidates = list(set(file_candidates))

        # for every affected template, find all files that use this template.
        # then, re-render them.
        for template in affected:
            # the leading / is necessary to not match incomplete template paths/names
            this_template = os.path.join(os.sep, template) + "." + config["PAGE_EXT"]
            for filename in file_candidates:
                if this_template in filename:
                    yield filename

    @staticmethod
    def _find_dependants(abspath):
        # we can't know how exactly the user included the file...
        relpath = abspath.replace(config["ROOT"]["DEV"], "")[1:]
        filename = os.path.basename(relpath)

        # ... but this is an educated guess.
        wanted = [f"[\"|\']{file}[\"|\']" for file in [abspath, relpath, filename]]

        # both the templates and the actual renderables need to be searched!
        to_be_searched = [config["PAGE_EXT"], "html"]

        # find every renderable or template that mentions the file we are interested in
        for ext in to_be_searched:
            for path in Path(config["ROOT"]["DEV"]).rglob("*." + ext):
                with open(path, "r") as file:
                    contents = file.read()
                    if any(re.search(regex, contents) for regex in wanted):
                        yield path

    @staticmethod
    def _get_web_path(path):
        """ get where a file is supposed to go. depends on the type """
        path = path.replace(config["ROOT"]["DEV"], "")                     # remove devroot if exists
        path = path.replace(config["ROOT"]["WEB"], "")                     # remove webroot if exists
        path = make_valid_path(config["ROOT"]["WEB"], path)                # add web root in front, args in back

        # Seperate path into its three components: dirname; file name; file extension
        dirname = os.path.dirname(path)
        filename, extension = os.path.splitext(os.path.basename(path))

        if extension == config["PAGE_EXT"]:
            filename = "index"
            extension = ".html"

            web_path = make_valid_path(dirname, filename) + extension
            return web_path

    @staticmethod
    def _get_parent_page(sub_page):
        """ return the path of the parent of a subpage """
        parent_dir = os.path.dirname(os.path.dirname(sub_page))  # equals the dir of the parent
        parent_page = str(next(Path(parent_dir).rglob("*." + config["PAGE_EXT"])))
        return parent_page

    @staticmethod
    def _delete(path):
        """ delete a file or dir """
        if os.path.exists(path):
            if os.path.isfile(path):
                os.remove(path)
            elif os.path.isdir(path):
                shutil.rmtree(path)

    @staticmethod
    def _move(fro, to):
        """ move a file or dir """
        os.makedirs(os.path.dirname(to), exist_ok=True)
        shutil.move(fro, to)
