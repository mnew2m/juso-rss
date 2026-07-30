from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator

fg = FeedGenerator()
fg.title('주소정보누리집 공지사항')
fg.link(href='https://juso.go.kr/ahh/ahhNotifyBoardList', rel='alternate')
fg.description('juso.go.kr 자동 생성 RSS')

url = 'https://juso.go.kr/ahh/ahhNotifyBoardList'

try:
    with sync_playwright() as p:
        # 헤드리스 크롬 브라우저 실행
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # 페이지 이동 및 네트워크 대기 (JS 렌더링 완료까지)
        page.goto(url, wait_until='networkidle', timeout=30000)
        
        # 렌더링된 최종 HTML 가져오기
        html = page.content()
        browser.close()

    soup = BeautifulSoup(html, 'html.parser')
    
    # juso.go.kr 게시판 항목 파싱 (a 태그 중 게시글 찾기)
    articles = soup.select('table tbody tr')
    count = 0

    for row in articles:
        a_tag = row.select_one('a')
        if a_tag:
            title = a_tag.get_text(strip=True)
            if title and len(title) > 2:
                fe = fg.add_entry()
                fe.title(title)
                fe.link(href=url)
                fe.guid(f"juso-{hash(title)}", permalink=False)
                count += 1

    if count == 0:
        fe = fg.add_entry()
        fe.title("[확인필요] 게시판 요소를 찾지 못함 (HTML 구조 확인 필요)")
        fe.link(href=url)
        fe.guid("juso-no-items", permalink=False)

except Exception as e:
    fe = fg.add_entry()
    fe.title(f"[에러 발생] {e}")
    fe.link(href=url)
    fe.guid("juso-error", permalink=False)

fg.rss_file('rss.xml')