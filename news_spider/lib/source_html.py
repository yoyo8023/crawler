# coding:utf8


def get_tag_html(soup, tag):
    """
    获取html标签中的元素
    :param tag:标签
    :param soup: BeautifulSoup对象
    """
    em_select = soup.select(tag)
    if em_select:
        return em_select[0].get_text()
    else:
        return ''
