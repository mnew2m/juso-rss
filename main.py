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
        # 브라우저 옵션 설정 (보안 경고 무시)
        browser = p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-setuid-sandbox'])
        context = browser.new_context(
            ignore_https_errors=True,
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
        )
        
        page = context.new_page()
        
        # 속도 향상을 위해 이미지, 폰트, CSS 차단
        page.route("**/*.{png,jpg,jpeg,svg,gif,woff,woff2,css}", lambda route: route.abort())

        # domcontentloaded 기준으로 대기 조건 변경 (타임아웃 60초로 확대)
        page.goto(url, wait_until='domcontentloaded', timeout=60000)
        
        # 게시판 테이블 요소가 들어올 때까지 최대 10초 추가 대기
        try:
            page.wait_for_selector('table', timeout=10000)
        except:
            pass

        html = page.content()
        browser.close()

    soup = BeautifulSoup(html, 'html.parser')
    
    # juso.go.kr 게시판 항목 파싱
    articles = soup.select('table tbody tr')
    count = 0

    for row in articles:
        a_tag = row.select_one('a')
        if a_tag:
            title = a_tag.get_text(strip=True)
            # 메뉴나 의미없는 텍스트 제외
            if title and len(title) > 2 and '검색' not in title:
                fe = fg.add_entry()
                fe.title(title)
                fe.link(href=url)
                fe.guid(f"juso-{hash(title)}", permalink=False)
                count += 1

    if count == 0:
        fe = fg.add_entry()
        fe.title("[확인필요] 페이지는 로드되었으나 게시글 목록이 비어있음")
        fe.link(href=url)
        fe.guid("juso-no-items", permalink=False)

except Exception as e:
    fe = fg.add_entry()
    fe.title(f"[에러 발생] {e}")
    fe.link(href=url)
    fe.guid("juso-error", permalink=False)

fg.rss_file('rss.xml')