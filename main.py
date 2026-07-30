import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator

# 1. RSS 기본 정보 세팅
fg = FeedGenerator()
fg.title('주소정보누리집 공지사항')
fg.link(href='https://juso.go.kr/ahh/ahhNotifyBoardList', rel='alternate')
fg.description('juso.go.kr 자동 생성 RSS')

# 2. 웹페이지 요청 (User-Agent 설정)
url = 'https://juso.go.kr/ahh/ahhNotifyBoardList'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

try:
    response = requests.get(url, headers=headers, verify=False, timeout=10)
    soup = BeautifulSoup(response.text, 'html.parser')

    # 게시판 테이블 행 추출 (juso.go.kr 게시판 구조)
    rows = soup.select('table tbody tr')
    
    for row in rows:
        # 제목 링크 태그 찾기
        a_tag = row.select_one('td.a_left a') or row.select_one('a')
        if a_tag:
            title = a_tag.get_text(strip=True)
            if title:
                fe = fg.add_entry()
                fe.title(title)
                fe.link(href=url)
except Exception as e:
    print(f"Error fetching data: {e}")

# 3. RSS 파일 저장
fg.rss_file('rss.xml')