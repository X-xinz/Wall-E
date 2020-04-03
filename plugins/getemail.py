import poplib
import datetime
import email
from robot.sdk.AbstractPlugin import AbstractPlugin
from email.parser import Parser
from email.header import decode_header
from email.utils import parseaddr
from robot import config, logging, statistic

logger = logging.getLogger(__name__)


class Plugin(AbstractPlugin):

    SLUG = 'email_get'

    IS_IMMERSIVE = 'False'

    def __init__(self, con):
        self.con = con
        self.email_address = config.get(
            '/email/email_address', '2381324877@qq.com')
        self.email_password = config.get(
            '/email/email_password', 'mnupufpoaclnecdh')
        self.pop_server_host = config.get(
            '/email/pop_server_host', 'pop.qq.com')
        self.pop_server_port = config.get('/email/pop_server_port', 995)
        self.read_numb = config.get('/email/read_numb', 5)
        self.e_text = config.get('/email/e_text', False)

    def handle(self, query, parsed):
        email_address = self.email_address
        email_password = self.email_password
        pop_server_host = self.pop_server_host
        pop_server_port = self.pop_server_port

        try:
            # 连接pop服务器。如果没有使用SSL，将POP3_SSL()改成POP3()即可其他都不需要做改动
            email_server = poplib.POP3_SSL(
                host=pop_server_host, port=pop_server_port, timeout=10)
            logger.debug(
                "pop3----connect server success, now will check username")
        except:
            logger.error(
                "pop3----sorry the given email server address connect time out")
            exit(1)
        try:

            email_server.user(email_address)
            logger.debug("pop3----username exist, now will check password")
        except:
            logger.error(
                "pop3----sorry the given email address seem do not exist")
            exit(1)
        try:
            # 验证邮箱密码是否正确
            email_server.pass_(email_password)
            logger.debug("pop3----password correct,now will list email")
        except:
            logger.error(
                "pop3----sorry the given username seem do not correct")
            exit(1)

        # 邮箱中其收到的邮件的数量
        email_count = len(email_server.list()[1])
        response = "您一共有"+str(email_count)+"封邮件,已为您展示最新的"+self.read_numb+"封"
        self.con.say(response, True)

        # list()返回所有邮件的编号:
        resp, mails, octets = email_server.list()
        na = int(self.read_numb)
        # 遍历所有的邮件
        for i in range(1, na + 1):

            # 通过retr(index)读取第index封邮件的内容；这里读取最后一封，也即最新收到的那一封邮件
            resp, lines, octets = email_server.retr(email_count-na+i)

            # lines是邮件内容，列表形式使用join拼成一个byte变量
            email_content = b'\r\n'.join(lines)
            try:
                # 再将邮件内容由byte转成str类型
                email_content = email_content.decode('utf-8')

            except Exception as e:
                logger.error(str(e))
                continue
            # # 将str类型转换成<class 'email.message.Message'>
            # msg = email.message_from_string(email_content)
            msg = Parser().parsestr(email_content)
            print('～～～～～～～～～～～～～～～～～～～  华丽分隔符  ～～～～～～～～～～～～～～～')
        
            # 写入邮件内容到文件
            self.parse_email(msg, 0)

        # 关闭连接
        email_server.close()

    # indent用于缩进显示:
    def parse_email(self, msg, indent):

        if indent == 0:
            # 邮件的From, To, Subject存在于根对象上:
            for header in ['From', 'To', 'Subject']:
                value = msg.get(header, '')
                if value:
                    if header == 'Subject':
                        # 需要解码Subject字符串:
                        value = self.decode_str(value)
                    else:
                        # 需要解码Email地址:
                        hdr, addr = parseaddr(value)
                        name = self.decode_str(hdr)
                        value = u'%s <%s>' % (name, addr)
                print('%s%s: %s' % ('  ' * indent, header, value))
                """
                From: 网易帐号中心  <passport@service.netease.com>
                To:  <m1476917158
                Subject: 重置成功
                """
        if (msg.is_multipart()):
            # 如果邮件对象是一个MIMEMultipart,
            # get_payload()返回list，包含所有的子对象:
            parts = msg.get_payload()

            for _n, part in enumerate(parts):
                # 递归打印每一个子对象:
                return self.parse_email(part, indent + 1)

        else:
            if self.e_text == True:
                # 邮件对象不是一个MIMEMultipart,
                # 就根据content_type判断:
                content_type = msg.get_content_type()
                if content_type == 'text/plain' or content_type == 'text/html':
                    # 纯文本或HTML内容:
                    content = msg.get_payload(decode=True)
                    # 要检测文本编码:
                    charset = self.guess_charset(msg)
                    if charset:
                        content = content.decode(charset)

                    print('%sText: %s' % ('  ' * indent, content))
                else:
                    # 不是文本，作为附件处理:
                    print('%sAttachment: %s' % ('  ' * indent, content_type))

    # 解码
    def decode_str(self, s):
        value, charset = decode_header(s)[0]
        if charset:
            value = value.decode(charset)
        return value

    # 猜测字符编码
    def guess_charset(self, msg):
        # 先从msg对象获取编码:
        charset = msg.get_charset()
        if charset is None:
            # 如果获取不到，再从Content-Type字段获取:
            content_type = msg.get('Content-Type', '').lower()
            for item in content_type.split(';'):
                item = item.strip()
                if item.startswith('charset'):
                    charset = item.split('=')[1]
                    break
        return charset

    def isValid(self, query, parsed):
        return '邮件' in query

