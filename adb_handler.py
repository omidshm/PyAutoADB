import logging
import subprocess
import time
from xml.etree import ElementTree


class ADBDevice:
    def __init__(
        self,
        port: int,
        host: str = "localhost",
    ):
        self.adb_port = port
        self.adb_host = host
        self.window_root = ""
        self.last_formatted_result = None
        # Connect to instance
        self.adb_connect()

    # done
    def set_command(self, adb_cmd: str):
        """
        Sets the command for ADB by splitting the input string and inserting the ADB port if it is not None.

        Args:
            adb_cmd (str): The command string to be set for ADB.

        Returns:
            str: The modified command string with the ADB port inserted if it is not None.
        """

        adb_cmd = adb_cmd.split()
        if not self.adb_port == None:
            adb_cmd.insert(1, f"-s localhost:{self.adb_port}")
        adb_cmd = " ".join(adb_cmd)
        return adb_cmd

    def adb_connect(self, auto: bool = False, default_instance: int = 999) -> bool:
        """
        Connects to an ADB instance using the specified port. If no port is specified, attempts to connect to the default ADB instance.

        Args:
            auto (bool, optional): Whether to automatically select the ADB instance. Defaults to False.
            default_instance (int, optional): The index of the default ADB instance to connect to. Defaults to 999.

        Returns:
            bool: True if the connection was successful, False otherwise.

        Raises:
            Exception: If the connection to the ADB instance fails.

        TODO:
            - Make it smarter to save active and running ports into the Environment variables
            - Detect automatically what port should use now
        """
        if self.adb_port:
            # TODO: make it smarter to save working and busy ports into the Environment variables
            # TODO: detect automatically what port should use now
            """adb_instances = port_finder()

            if not auto:
                if default_instance < 999:
                    selected_port = adb_instances[default_instance - 1]
                else:
                    for i, inctance_name in enumerate(adb_instances):
                        print(f"{i}: {inctance_name}")
                    user_choice = int(input("Please select a port: "))
                    selected_port = adb_instances[user_choice]
            else:
                selected_port = adb_instances[0]
            """
            adb_addr = f"localhost:{self.adb_port}"
            result = subprocess.run(["adb", "connect", adb_addr], capture_output=True)
            formatted_result = result.stdout.decode("utf-8")

            # Check Result
            if "connected" in formatted_result:
                logging.info(f"adb connected to {adb_addr} successfully")
                return True
            else:
                raise Exception("ADB cannot connect to Emulator. check the port")

    def bnds_to_tuple(self, bnd_str: str):
        bnd_str = bnd_str.replace("][", ",").replace("[", "").replace("]", "")
        bnd_str = tuple(map(int, bnd_str.split(",")))
        return bnd_str

    def refresh_root_window(self):
        logging.debug("root window refreshed")
        self.window_root = self.get_window()

    def check_xpath_exists(self, element_xpath):
        root = self.window_root

        element = root.find(element_xpath)

        if element is not None:
            return True
        else:
            return False

    def get_bnds(self, xpath):
        root = self.window_root

        element = root.find(xpath)

        if element is not None:

            # Get the bounds of the element
            bounds = element.get("bounds")

            return bounds
        else:
            raise Exception("Cannot found the bounds")

    # make it async
    def wait_for_change(self):
        while True:
            old_root = self.window_root

            self.refresh_root_window()

            if old_root == self.window_root:
                logging.info("The window doesn't change go for next time")
            else:
                logging.info("The window transmitted Successfully")
                return True

    def get_window(self) -> ElementTree.Element:
        for _ in range(3):
            try:
                command = self.set_command(f"adb shell uiautomator dump /sdcard/window_dump.xml")
                result = subprocess.run(command, capture_output=True)
                self.last_formatted_result = result.stdout.decode("utf-8")

                logging.debug(self.last_formatted_result)
                adb_identifier = self.adb_port

                command = self.set_command(
                    f"adb pull /sdcard/window_dump.xml file{adb_identifier}.xml"
                )
                subprocess.run(command)

                tree = ElementTree.parse(f"file{adb_identifier}.xml")
                window_root = tree.getroot()

                return window_root
            except Exception as e:
                logging.critical(e)
                time.sleep(0.7)

    def get_xpath_text(self, element_xpath: str) -> str | None:
        # Get Xpath Str
        root = self.window_root

        element = root.find(element_xpath)

        if element is not None:
            text = element.get("text")

            return text
        else:
            logging.debug(f"cannot find any text for: {element_xpath}")
            return None

    def get_xpath_content_desc(self, input_name: str) -> str:
        # Get Xpath Str
        root = self.window_root

        element = root.find(input_name)

        if element is not None:
            text = element.get("content-desc")

            return text
        else:
            return None

    def press_backspace(self, number_of_backspace: int = 3) -> None:
        logging.info(f"Backspace going to press {number_of_backspace} times")
        command = self.set_command(f"adb shell input keyevent KEYCODE_MOVE_END")
        subprocess.run(command)

        for _ in range(number_of_backspace):
            command = self.set_command(f"adb shell input keyevent --longpress KEYCODE_DEL")
            subprocess.run(command)

    def clear_selected_input(self, input_name_xpath: str) -> bool:
        # input_name: xpath
        input_text = self.get_xpath_text(input_name_xpath)

        if input_text:
            command = self.set_command(f"adb shell input keyevent KEYCODE_MOVE_END")
            subprocess.run(command)

            for _ in range(int((len(input_text) / 2) + 5)):
                command = self.set_command(f"adb shell input keyevent --longpress KEYCODE_DEL")
                subprocess.run(command)

            logging.info(f"Clear executed for {input_name_xpath}, text is {input_text}")
            return True
        else:
            return True

    def get_list_files(self, path):
        command = self.set_command(f"adb shell ls {path}")
        result = subprocess.check_output(command)
        formatted_result = result.decode("utf-8")
        lines = formatted_result.splitlines()

        return lines

    def fast_clear_selected_input(self, input_name_xpath: str) -> bool:
        # input_name: xpath
        input_text = self.get_xpath_text(input_name_xpath)

        if input_text:
            command = self.set_command(f"adb shell input keyevent KEYCODE_MOVE_END")
            subprocess.run(command)

            for _ in range(int((len(input_text)) + 4)):
                command = self.set_command(f"adb shell input keyevent KEYCODE_DEL")
                subprocess.run(command)
            logging.info(f"fast clear executed for {input_name_xpath}, text is {input_text}")

            return True
        else:
            return True

    def touch_xpath(self, xpath):
        # Tested
        root = self.window_root

        element = root.find(xpath)

        if element is not None:

            # Get the bounds of the element
            bounds = element.get("bounds")

            if bounds is not None:
                numbers = re.findall(r"\d+", bounds)
                numbers = [int(num) for num in numbers]
                # Calculate the center of the element
                x1, y1, x2, y2 = numbers
                x = (x1 + x2) // 2
                y = (y1 + y2) // 2

                # Simulate a touch event at the center of the element
                command = self.set_command(f"adb shell input tap {x} {y}")
                subprocess.run(command)

                logging.info(f"adb shell input tap {x} {y} executed.")
                return True
            else:
                logging.info(f"adb shell input tap {x} {y} failed.")
                raise Exception(f"Cannot touch the {x} {y}")
        else:
            raise Exception(f"element not found to touch.")

    def pull_file(self, src_path: str, dest_path: str) -> str | bool:
        command = self.set_command(f"adb pull {src_path} {dest_path}")
        try:
            subprocess.run(command)
        except Exception as e:
            ...

    def touch_exact_point(self, x: int, y: int):
        command = self.set_command(f"adb shell input tap {x} {y}")

        try:
            subprocess.run(command, shell=True)
            logging.info(f"{self.adb_port} adb shell input tap {x} {y} executed.")
            return True
        except:
            logging.info(f"{self.adb_port} adb shell input tap {x} {y} failed.")
            raise Exception(f"Cannot touch the {x} {y}")

    def touch_bnds(self, bounds: str):
        correct_bounds = self.bnds_to_tuple(bounds)

        numbers = [int(num) for num in correct_bounds]
        # Calculate the center of the element
        x1, y1, x2, y2 = numbers
        x = (x1 + x2) // 2
        y = (y1 + y2) // 2

        # Simulate a touch event at the center of the element
        command = self.set_command(f"adb shell input tap {x} {y}")

        try:
            subprocess.run(command, shell=True)
            logging.info(f"{self.adb_port} adb shell input tap {x} {y} bounds: {bounds}")
            return True
        except:
            logging.info(f"{self.adb_port} adb shell input tap {x} {y} failed. bounds: {bounds}")
            raise Exception(f"Cannot touch the {x} {y}")

    def check_xpath(self, xpath, check_text):
        element_txt = self.get_xpath_text(xpath)

        if element_txt == check_text:
            return True
        else:
            return False

    def check_bnds(self, bounds: str, check_text):
        full_xpath = f".//*[@bounds='{bounds}']"

        element_txt = self.get_xpath_text(full_xpath)
        if element_txt == check_text:
            return True
        else:
            return False

    def check_text_exist(self, text: str) -> bool:
        xpath = f".//node[@text = '{text}']"
        element_txt = self.get_xpath_text(xpath)

        if element_txt == text:
            return True
        else:
            return False

    def replace_space_str(self, input_string: str) -> str:
        # replace " " with "\ " and return it
        return input_string.replace(" ", "\\ ")

    def write_text(self, text: str):
        standard_text = self.replace_space_str(str(text))
        command = self.set_command(f'adb shell input text "{standard_text}"')
        try:
            logging.info(f"Try to write {standard_text} fast")
            subprocess.run(command)
            return True
        except:
            raise Exception("Cannot Write your text with ADB")

    def split_into_chunks(self, input_string) -> list:
        # Check if the input string is empty
        if not input_string:
            return []

        # Use list comprehension to create 2-character chunks
        chunks = [input_string[i : i + 2] for i in range(0, len(input_string), 2)]

        return chunks

    def write_text_slow(self, text: str):
        standard_text = self.replace_space_str(text)
        text_chunks = self.split_into_chunks(standard_text)

        commands_chain = [
            self.set_command(f'adb shell input text "{standard_text}"')
            for standard_text in text_chunks
        ]
        try:
            logging.info(f"Try to write {standard_text} slowly")
            for _ in commands_chain:
                subprocess.run(_)
                time.sleep(0.1)
            return True
        except:
            raise Exception("Cannot Write your text with ADB")

    def open_app(self, packagename: str) -> None:
        command = self.set_command(
            f"adb shell monkey -p {packagename} -c android.intent.category.LAUNCHER 1"
        )
        result = subprocess.check_output(command, text=True)
        logging.info(f"port{self.adb_port} Open the {packagename}")

    def close_app(self, packagename: str) -> None:
        command = self.set_command(f"adb shell am force-stop {packagename}")
        result = subprocess.check_output(command)
        logging.info(f"port{self.adb_port} {packagename} force-closed")

    def press_back(self):
        command = self.set_command("adb shell input keyevent KEYCODE_BACK")
        result = subprocess.check_output(command)

        logging.info(f"Back key pressed")

    # All Tested before this section

    def get_notif_list(self) -> list[str]:
        command = self.set_command("adb shell dumpsys notification --noredact")
        result = subprocess.check_output(command)

        notif_lines = []
        for line in result.splitlines():
            notif_lines.append(line.decode())

        return notif_lines

    def find_element_by_regex(self) -> ElementTree.Element:
        root = ElementTree.fromstring(self.window_root)

        # Find the element using XPath
        pattern = r"exposed via (\d+)"
        for element in root.iter():
            if pattern.match(element.tag):
                print(element.text)

    def install_app(self, apk_path: str, package_name: str = "org.telegram.messenger.web") -> bool:

        command = self.set_command(f"adb install -g -r {apk_path}")
        logging.info(f"Try to install {apk_path}")

        for _ in range(7):
            try:
                result = subprocess.check_output(command, timeout=60, text=True)

                if "Success" in result:
                    return True
            except Exception as e:
                raise Exception(f"install Exception: {e}")

            time.sleep(0.5)
            command = self.set_command(f"adb shell pm list packages")
            result = subprocess.check_output(command, text=True)

            if package_name in result:
                return True

        raise Exception(f"error on install : {result}")
        return False

    def uninstall_app(self, package_name: str) -> bool:

        command = self.set_command(f"adb uninstall {package_name}")

        result = subprocess.check_output(command, timeout=50, text=True)

        logging.warning(f"uninstalling result {result}")
        # Check Result
        if "Success" in result:
            return True
        else:
            return False

    def clear_data(self, package_name: str) -> bool:

        command = self.set_command(f"adb shell pm clear {package_name}")

        result = subprocess.check_output(command, timeout=50, text=True)

        logging.warning(f"package {package_name} data cleared. result: {result}")
        # Check Result
        if "Success" in result:
            return True
        else:
            return False

    def grant_permission(self, pkg_name: str, permission: str) -> bool:

        command = self.set_command(f"adb shell pm grant {pkg_name} {permission}")

        result = subprocess.check_output(command, timeout=20, text=True)
        logging.info(f"{permission} permission granted {result}")
        # Check Result
        if "Success" in result:
            return True
        else:
            return False

    def grant_call_contact_permissions(self, package_name: str):
        command = self.set_command(
            f"adb shell pm grant {package_name} android.permission.READ_PHONE_STATE"
        )

        result = subprocess.check_output(command, timeout=20, text=True)
        logging.info(f"READ_PHONE_STATE permission granted {result}")
        command = self.set_command(
            f"adb shell pm grant {package_name} android.permission.READ_CONTACTS"
        )

        result = subprocess.check_output(command, timeout=20, text=True)
        logging.info(f"READ_CONTACTS permission granted {result}")

    def grant_mic_permissions(self, package_name: str):
        command = self.set_command(
            f"adb shell pm grant {package_name} android.permission.RECORD_AUDIO"
        )

        result = subprocess.check_output(command, timeout=20, text=True)
        logging.info(f"RECORD_AUDIO permission granted {result}")

    def get_xpath_by_bounds(self, bounds: str) -> str:
        return f".//node[@bounds='{bounds}' ]"

    def get_xpath_by_resource_id(self, resource_id: str) -> str:
        return f".//node[@resource-id='{resource_id}' ]"

    def get_xpath_by_text(self, text: str) -> str:
        return f".//node[@text='{text}' ]"

    def take_screenshot(self) -> str:
        take_shot_command = self.set_command("adb shell screencap -p /sdcard/screenshot.png")

        result = subprocess.run(take_shot_command, capture_output=True)

        filename = f"screenshot{self.adb_port}.png"
        pull_screenshot_command = self.set_command(f"adb pull /sdcard/screenshot.png {filename}")
        logging.info(f"screenshot saved as {filename}")

        result = subprocess.run(pull_screenshot_command, capture_output=True)

        return filename

    def open_deep_link(self, url: str, default_pkg: str = "org.thunderdog.challegram"):
        command_string = f"adb shell am start -a android.intent.action.VIEW -d {url} {default_pkg}"

        deep_link_command = self.set_command(command_string)

        subprocess.run(deep_link_command, capture_output=True)

    def scroll_down(self):
        command_string = "adb shell input swipe 150 400 150 150"

        scroll_down_command = self.set_command(command_string)

        subprocess.run(scroll_down_command, capture_output=True)

    def scroll_up(self):
        command_string = "adb shell input swipe 150 150 150 400"

        scroll_down_command = self.set_command(command_string)

        subprocess.run(scroll_down_command, capture_output=True)

    def get_current_focus_window(self) -> str:

        command_string = "adb shell dumpsys window displays | grep -E 'mCurrentFocus'"

        command = self.set_command(command_string)

        result = subprocess.check_output(command, timeout=20, text=True)

        return result
