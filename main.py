import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
import urllib3

# SSL 경고창 비활성화
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 1. RSS 피드 기본 정보 세팅
fg = FeedGenerator()
fg.title('주소정보누리집 공지사항')
fg.link(href='https://juso.go.kr/ahh/ahhNotifyBoardList', rel='alternate')
fg.description('juso.go.kr 자동 생성 RSS')

# 2. 웹페이지 요청 (브라우저인 척 위장)
url = 'https://juso.go.kr/ahh/ahhNotifyBoardList'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Referer': 'https://juso.go.kr/'
}

try:
    response = requests.get(url, headers=headers, verify=False, timeout=15)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, 'html.parser')

    # juso.go.kr 게시판 글 목록 파싱 (모든 a 태그 중 게시글 제목 추출)
    # 보통 게시판의 제목 링크에는 onclick이나 특정 class가 들어가 있습니다.
    articles = soup.find_all('a')
    
    count = 0
    for a in articles:
        title = a.get_text(strip=True)
        # 글 제목으로 추정되는 길이 및 조건 필터링 (메뉴 링크 제외)
        if title and len(title) > 5 and not any(k in title for k in ['로그인', '회원가입', '사이트맵', '저작권', '개인정보']):
            # 게시글 개수 15개로 제한
            if count >= 15:
                break
                
            fe = fg.add_entry()
            fe.title(title)
            fe.link(href=url)
            # GUID(고유 식별자) 부여 - Teams가 새 글을 구분하는 기준
            fe.guid(f"juso-notice-{hash(title)}", permalink=False)
            count += 1

except Exception as e:
    print(f"Error fetching data: {e}")

# 3. RSS 파일 저장
fg.rss_file('rss.xml')