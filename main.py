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
        browser = p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-setuid-sandbox'])
        context = browser.new_context(
            ignore_https_errors=True,
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
        )
        
        page = context.new_page()
        # 속도를 위해 이미지/폰트만 차단 (스크립트/스타일은 실행되도록 허용)
        page.route("**/*.{png,jpg,jpeg,svg,gif,woff,woff2}", lambda route: route.abort())

        # 페이지 접속
        page.goto(url, wait_until='domcontentloaded', timeout=60000)
        
        # AJAX/JS 데이터 로딩 대기 (3초)
        page.wait_for_timeout(3000)

        html = page.content()
        browser.close()

    soup = BeautifulSoup(html, 'html.parser')
    
    # juso.go.kr 게시판의 다양한 구조에 대응
    # 1) table 기반, 2) ul/li 기반, 3) a 태그 기반 전체 탐색
    articles = soup.select('table tbody tr') or soup.select('.board_list li') or soup.select('ul.list li')
    
    count = 0
    if articles:
        for row in articles:
            a_tag = row.select_one('a')
            if a_tag:
                title = a_tag.get_text(strip=True)
                if title and len(title) > 3:
                    fe = fg.add_entry()
                    fe.title(title)
                    fe.link(href=url)
                    fe.guid(f"juso-{hash(title)}", permalink=False)
                    count += 1

    # 만약 특정 구조를 찾지 못했다면 전체 a 태그 중 게시글 패턴 탐색
    if count == 0:
        all_links = soup.find_all('a')
        for a in all_links:
            title = a.get_text(strip=True)
            # 게시글 제목 특성 조건 (길이 8자 이상, 일반 메뉴명 제외)
            if title and len(title) >= 8 and not any(x in title for x in ['주소정보누리집', '개인정보처리방침', '저작권', '바로가기', '로그인']):
                fe = fg.add_entry()
                fe.title(title)
                fe.link(href=url)
                fe.guid(f"juso-{hash(title)}", permalink=False)
                count += 1
                if count >= 15:  # 최대 15개까지만 가져오기
                    break

    if count == 0:
        fe = fg.add_entry()
        fe.title("[확인필요] HTML 텍스트 파싱 실패")
        fe.link(href=url)
        fe.guid("juso-no-items", permalink=False)

except Exception as e:
    fe = fg.add_entry()
    fe.title(f"[에러 발생] {e}")
    fe.link(href=url)
    fe.guid("juso-error", permalink=False)

fg.rss_file('rss.xml')