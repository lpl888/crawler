import time
import json

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class ProjectCrawler:
    def __init__(self, base_url, start_page, end_page):
        self.base_url = base_url
        self.start_page = start_page
        self.end_page = end_page
        self.driver = None
        self.all_projects = []

    def start_driver(self):
        """브라우저 드라이버를 시작"""
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

    def stop_driver(self):
        """브라우저 드라이버를 종료"""
        if self.driver:
            self.driver.quit()

    def load_page(self, page_number):
        """지정된 페이지로 이동"""
        url = f"{self.base_url}?page={page_number}&sm=5"
        self.driver.get(url)
        time.sleep(1)  # 페이지가 로드될 시간을 기다림
        print(f"---{page_number} page loaded")
        

    def extract_project_data(self, li):
        """단일 프로젝트의 데이터를 추출"""
        try:
            # 모든 p 태그에서 기술 스택 추출
            # Title 추출
            title = li.find_element(By.CLASS_NAME, 'title').text.strip()

            # 예상 비용 추출
            cost = li.find_element(By.XPATH, ".//span[text()='예상비용']/following-sibling::b").text.strip()

            # 지원자 수 추출
            num_app = li.find_element(By.XPATH, ".//span[text()='지원자수']/following-sibling::b").text.strip()

            # 마감 일정 추출
            dead_line = li.find_element(By.XPATH, ".//span[text()='마감일정']/following-sibling::b").text.strip()

            project_data = {
                'title': title,
                'cost': cost,
                'num_app': num_app,
                'dead_line': dead_line
            }

            # print(project_data)

            return project_data

        except Exception as e:
            print(f"Error processing project: {e}")
            return None

    def scrape_projects(self):
        """지정된 페이지 범위 내에서 프로젝트를 크롤링"""
        self.start_driver()

        try:
            for page in range(self.start_page, self.end_page + 1):
                self.load_page(page)

                try:
                    ul_tag = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.CLASS_NAME, 'proj-list-item_new'))
                    )

                    li_tags = ul_tag.find_elements(By.TAG_NAME, 'li')

                    for li in li_tags:
                        project_data = self.extract_project_data(li)
                        if project_data:
                            self.all_projects.append(project_data)

                except Exception as e:
                    print(f"Error locating element on page {page}: {e}")
                    continue
                
                        
                if page % 100 == 0:
                    crawler.save_json()
                    print(f"---{page} page saved")

        finally:
            print(f"---{page} page crawled")
            self.stop_driver()

    def save_json(self, file_name='projects_add_contents.json'):
        """추출된 데이터를 JSON 파일로 저장"""
        with open(file_name, 'w', encoding='utf-8') as json_file:
            json.dump(self.all_projects, json_file, ensure_ascii=False, indent=4)

    def display_projects(self):
        """추출된 프로젝트 데이터를 출력"""
        for project in self.all_projects:
            print(project)


# 크롤러 실행
if __name__ == "__main__":
    base_url = "https://www.freemoa.net/m4/s41"
    start_page = 1
    end_page = 1

    crawler = ProjectCrawler(base_url, start_page, end_page)
    crawler.scrape_projects()