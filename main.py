import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

fg = FeedGenerator()
fg.title('주소정보누리집 공지사항')
fg.link(href='https://juso.go.kr/ahh/ahhNotifyBoardList', rel='alternate')
fg.description('juso.go.kr 자동 생성 RSS')

url = 'https://juso.go.kr/ahh/ahhNotifyBoardList'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
}

try:
    session = requests.Session()
    # 1. 메인페이지 방문하여 쿠키 획득
    session.get('https://juso.go.kr/main.do', headers=headers, verify=False, timeout=10)
    
    # 2. 게시판 페이지 요청
    response = session.get(url, headers=headers, verify=False, timeout=10)
    response.encoding = 'utf-8'
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # juso.go.kr 게시판 테이블 셀렉터 탐색
    rows = soup.select('table tbody tr')
    
    count = 0
    for row in rows:
        # 제목 텍스트 파싱 (보통 a 태그 또는 td 내 텍스트)
        a_tag = row.select_one('a')
        if a_tag:
            title = a_tag.get_text(strip=True)
            if title and len(title) > 2:
                fe = fg.add_entry()
                fe.title(title)
                fe.link(href=url)
                fe.guid(f"juso-{hash(title)}", permalink=False)
                count += 1

    # 만약 크롤링된 항목이 하나도 없다면 (디버깅용)
    if count == 0:
        fe = fg.add_entry()
        fe.title("[확인필요] juso.go.kr 데이터 크롤링 수집 실패 (셀렉터/보안 블록)")
        fe.link(href=url)
        fe.guid("juso-debug-fail", permalink=False)

except Exception as e:
    print(f"Error: {e}")
    fe = fg.add_entry()
    fe.title(f"[에러] RSS 생성 중 오류 발생: {e}")
    fe.link(href=url)

fg.rss_file('rss.xml')