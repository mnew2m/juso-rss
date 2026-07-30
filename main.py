import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator

# RSS 피드 기본 설정
fg = FeedGenerator()
fg.title('주소정보누리집 공지사항')
fg.link(href='https://juso.go.kr/ahh/ahhNotifyBoardList', rel='alternate')
fg.description('juso.go.kr 자동 생성 RSS')

# 주소정보누리집 게시판 요청 (SSL 검증 예외 처리 필요할 수 있음)
url = 'https://juso.go.kr/ahh/ahhNotifyBoardList'
headers = {'User-Agent': 'Mozilla/5.0'}
response = requests.get(url, headers=headers, verify=False)
soup = BeautifulSoup(response.text, 'html.parser')

# 게시판 항목 파싱 (juso.go.kr 게시판 테이블 구조)
rows = soup.select('table.tbl_list tbody tr')
for row in rows:
    cols = row.find_all('td')
    if len(cols) > 1:
        title_tag = cols[1].find('a')
        if title_tag:
            title = title_tag.get_text(strip=True)
            # 게시글 아이템 추가
            fe = fg.add_entry()
            fe.title(title)
            fe.link(href=url)

# rss.xml 파일로 저장
fg.rss_file('rss.xml')