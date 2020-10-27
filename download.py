#!/usr/bin/python3

from selenium import webdriver
from colorama import Fore, Style
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import os
import time

CHROMEDRIVER_PATH = '/usr/bin/chromedriver'
download_path = os.getcwd() + '/downloaded/'
starting_page_number = 1
final_page_number = 43

def setup_driver():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--incognito')
    prefs = {'profile.default_content_setting_values.automatic_downloads': 1,
             'download.default_directory': download_path}
    chrome_options.add_experimental_option("prefs", prefs)
    driver = webdriver.Chrome(CHROMEDRIVER_PATH, options=chrome_options)
    return driver


def is_download_complete(driver):
    '''
    Waits for the download to complete.
    '''
    if not driver.current_url.startswith("chrome://downloads"):
        driver.get("chrome://downloads/")
    return driver.execute_script("""
        var items = document.querySelector('downloads-manager')
            .shadowRoot.getElementById('downloadsList').items;
        if (items.every(e => e.state === "COMPLETE"))
            return items.map(e => e.fileUrl || e.file_url);
        """)


def get_download_pages(page_number):
    '''
    Returns a list of download page links to further download files using download_files().
    '''
    driver = setup_driver()
    # Set timeout for implicit wait to 5 seconds.
    driver.implicitly_wait(5)
    website = 'https://en.freedownloadmanager.org/Windows-PC/search/computer+store+exe+software/' + str(page_number)
    try:
        driver.get(website)
    except KeyboardInterrupt:
        print("\nExiting.")
        exit()
    except Exception as e:
        print("An error occured:")
        print(e)
        driver.quit()
        exit()

    try:
        WebDriverWait(driver, 3).until(
            EC.visibility_of_element_located(
                (By.CSS_SELECTOR, "a.prog_download"))
        )
    except KeyboardInterrupt:
        print("\nExiting.")
        exit()
    except TimeoutException:
        print(f"{Fore.YELLOW}[*] Page timed out or download links not found on the page.{Style.RESET_ALL}")
        driver.quit()
        return []
    except Exception as e:
        print("An error occured:")
        print(e)
        driver.quit()
        exit()

    # Fetching all 'Download' elements on the page-
    element_list = driver.find_elements_by_css_selector('a.prog_download')
    # Extracting the 'href' from those download elements-
    link_list = []
    for element in element_list:
        link = element.get_attribute('href')
        link_list.append(link)

    driver.quit()
    return link_list


def download_files(link_list):
    '''
    Gets a list of links from get_download_pages() and extracts final download links from them.
    '''
    driver = setup_driver()
    for link in link_list:
        try:
            driver.get(link)
        except KeyboardInterrupt:
            print("\nExiting.")
            exit()
        except TimeoutException:
            print(f"{Fore.YELLOW}[*] Page timed out.{Style.RESET_ALL}")
            continue
        except Exception as e:
            print("An error occured:")
            print(e)
            driver.quit()
            exit()

        try:
            WebDriverWait(driver, 3).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR,
                                                  "div.wrapper > div.content > div.left_container > div.top_wrapper > p.h1 > a"))
            )
        except KeyboardInterrupt:
            print("\nExiting.")
            exit()
        except TimeoutException:
            print(f"{Fore.YELLOW}[*] Page timed out or download link not found on the page.{Style.RESET_ALL}")
            continue
        except ConnectionError:
            # If page refuses connection, wait for 15 seconds and continue-
            print(
                f"{Fore.RED}[-] Page refused connection. Waiting for 15 seconds before continuing...{Style.RESET_ALL}")
            time.sleep(15)
            continue
        except Exception as e:
            print("An error occured while downloading:")
            print(e)
            # Wait 15 seconds to get around possible automation block-
            time.sleep(15)
            print(f"{Fore.YELLOW}[*] Continuing...{Style.RESET_ALL}")
            continue

        print(f"{Fore.GREEN}[+] Downloading file...{Style.RESET_ALL}")
        # Wait for the download to start-
        time.sleep(10)
        # Wait for the download to complete-
        WebDriverWait(driver, 120, 1).until(is_download_complete)

    driver.quit()


if __name__ == '__main__':
    try:
        if os.path.isdir(download_path):
            print(
                f"{Fore.RED}[-] Directory ./downloaded already exists. Please delete or move it.{Style.RESET_ALL}")
            exit()
        else:
            print(
                f"{Fore.GREEN}[+] Making directory './downloaded'{Style.RESET_ALL}")
            os.mkdir(download_path)
        for page_number in range(starting_page_number, final_page_number + 1):
            try:
                download_pages = get_download_pages(page_number)
                if len(download_pages) > 0:
                    download_files(download_pages)
                else:
                    print(
                        f"{Fore.RED}[-] Received empty list of download links. Moving on to next page...{Style.RESET_ALL}")
                    continue
            except Exception as e:
                # If any exception occurs, print it and move on to the next page number-
                print(f"{Fore.RED}[-] An exception occured:{Style.RESET_ALL}")
                print(e)
                continue
    except KeyboardInterrupt:
        print("\nExiting...")
        exit()