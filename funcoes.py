import smtplib
import sqlite3
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
import cv2


def cria_usuario(self):
    user = self.ids.email.text
    password = self.ids.senha.text
    if not user and not password:
        contenido_popup = BoxLayout(orientation='vertical', padding=10)
        contenido_popup.add_widget(Label(text='É obrigatório informar os dados para cadastro!'))
        popup = Popup(title='Cadastro de Usuário', content=contenido_popup, size_hint=(None, None), size=(1000, 200))
        popup.open()

    elif not user:
        contenido_popup = BoxLayout(orientation='vertical', padding=10)
        contenido_popup.add_widget(Label(text='É obrigatório cadastrar um email!'))
        popup = Popup(title='Cadastro de Usuário', content=contenido_popup, size_hint=(None, None), size=(1000, 200))
        popup.open()

    elif not password:
        contenido_popup = BoxLayout(orientation='vertical', padding=10)
        contenido_popup.add_widget(Label(text='É obrigatório cadastrar uma senha!'))
        popup = Popup(title='Cadastro de Usuário', content=contenido_popup, size_hint=(None, None), size=(1000, 200))
        popup.open()

    else:
        conn, cursor = conectar_banco_dados()
        registrar = registrar_usuario(cursor, user, password)
        fechar_conexao(conn)
        if registrar:
            contenido_popup = BoxLayout(orientation='vertical', padding=10)
            contenido_popup.add_widget(Label(text='Usuário cadastrado com sucesso!'))
            popup = Popup(title='Cadastro de Usuário', content=contenido_popup, size_hint=(None, None),
                          size=(1000, 200))
            popup.open()

        else:
            contenido_popup = BoxLayout(orientation='vertical', padding=10)
            contenido_popup.add_widget(Label(text='Usuário já cadastrado na base de dados!'))
            popup = Popup(title='Cadastro de Usuário', content=contenido_popup, size_hint=(None, None),
                          size=(1000, 200))
            popup.open()


def login(self):
    user = self.ids.email.text
    password = self.ids.senha.text
    if not user and not password:
        contenido_popup = BoxLayout(orientation='vertical', padding=10)
        contenido_popup.add_widget(Label(text='É obrigatório informar dados de acesso!'))
        popup = Popup(title='Login', content=contenido_popup, size_hint=(None, None), size=(1000, 200))
        popup.open()

    elif not user:
        contenido_popup = BoxLayout(orientation='vertical', padding=10)
        contenido_popup.add_widget(Label(text='O email é obrigatório!'))
        popup = Popup(title='Login', content=contenido_popup, size_hint=(None, None), size=(1000, 200))
        popup.open()

    elif not password:
        contenido_popup = BoxLayout(orientation='vertical', padding=10)
        contenido_popup.add_widget(Label(text='A senha é obrigatória!'))
        popup = Popup(title='Login', content=contenido_popup, size_hint=(None, None), size=(1000, 200))
        popup.open()

    else:
        # conecta a banco de dados
        conn, cursor = conectar_banco_dados()
        loga = autenticar_usuario(cursor, user, password)
        # Executa e Fecha a conexão com o banco de dados
        fechar_conexao(conn)
        if loga:
            # Ação a executar após autenticar com sucesso
            self.manager.current = 'consulta'  # Abre a tela de consulta
            self.ids.email.text = ""
            self.ids.senha.text = ""

        else:
            contenido_popup = BoxLayout(orientation='vertical', padding=10)
            contenido_popup.add_widget(Label(text='Falha de Autenticação!'))
            popup = Popup(title='Login', content=contenido_popup, size_hint=(None, None), size=(1000, 200))
            popup.open()

            self.ids.email.text = ""
            self.ids.senha.text = ""


def send_password_reset_email(self):
    user = self.ids.email.text
    password = ""
    if not user:
        contenido_popup = BoxLayout(orientation='vertical', padding=10)
        contenido_popup.add_widget(Label(text='Informe um email para recuperar a senha!'))
        popup = Popup(title='Recuperar Senha', content=contenido_popup, size_hint=(None, None), size=(1000, 200))
        popup.open()

    else:
        conn, cursor = conectar_banco_dados()
        nova_senha(cursor, user, password)
        fechar_conexao(conn)


def criar_tabela_usuarios(cursor):
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user VARCHAR (100) NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    ''')


def registrar_usuario(cursor, user, password):
    try:
        cursor.execute("INSERT INTO usuarios (user, password) VALUES (?, ?)", (user, password))
    except sqlite3.IntegrityError:
        return False
    else:
        return True


def autenticar_usuario(cursor, user, password):
    cursor.execute("SELECT * FROM usuarios WHERE user = ? AND password = ?", (user, password))
    return cursor.fetchone() is not None


def nova_senha(cursor, user, password):
    cursor.execute("SELECT password FROM usuarios WHERE user = ? AND password <> ?", (user, password))
    result = cursor.fetchone()
    if result is not None:
        # Acessando os dados retornados
        valor = result[0]
        # Enviar e-mail com link de redefinição de senha, utilizando o valor retornado
        sender_email = "marcelosds@gmail.com"
        sender_password = "ylpjujwzwsoeczjd"
        receiver_email = user
        subject = "Recuperação de senha"
        message = f"Olá,\n\nSua senha de acesso ao APP é: {valor}\n\n" \
                  f"Se você não solicitou a recuperação de senha, ignore este e-mail.\n\n" \
                  f"Atenciosamente,\nEquipe de suporte"

        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = receiver_email
        msg['Subject'] = subject
        msg.attach(MIMEText(message, 'plain'))

        try:
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login(sender_email, sender_password)
                server.sendmail(sender_email, receiver_email, msg.as_string())
            contenido_popup = BoxLayout(orientation='vertical', padding=10)
            contenido_popup.add_widget(Label(text='E-mail enviado com sucesso.'))
            popup = Popup(title='Recuperar Senha', content=contenido_popup, size_hint=(None, None), size=(1000, 200))
            popup.open()
        except smtplib.SMTPException:
            contenido_popup = BoxLayout(orientation='vertical', padding=10)
            contenido_popup.add_widget(Label(text='Ocorreu um erro ao enviar o e-mail.'))
            popup = Popup(title='Recuperar Senha', content=contenido_popup, size_hint=(None, None), size=(1000, 200))
            popup.open()


    else:
        contenido_popup = BoxLayout(orientation='vertical', padding=10)
        contenido_popup.add_widget(Label(text='Dados de cadastro não localizados!'))
        popup = Popup(title='Recuperar Senha', content=contenido_popup, size_hint=(None, None), size=(1000, 200))
        popup.open()


def conectar_banco_dados():
    # Conectando ao banco de dados (cria o arquivo se não existir)
    conn = sqlite3.connect('dados.db')

    # Criando um cursor para executar comandos SQL
    cursor = conn.cursor()

    # Criando a tabela de usuários, se não existir
    criar_tabela_usuarios(cursor)

    return conn, cursor


def fechar_conexao(conn):
    conn.commit()
    conn.close()


# ANALISAR IMAGEM
def analisar(self):
    def center(x, y, w, h):
        x1 = int(w / 2)
        y1 = int(h / 2)
        cx = x + x1
        cy = y + y1
        return cx, cy

    cap = cv2.VideoCapture(0)

    fgbg = cv2.createBackgroundSubtractorMOG2()

    detects = []

    posL = 250
    offset = 30

    xy1 = (10, posL)
    xy2 = (620, posL)

    total = 0
    up = 0
    down = 0

    while 1:
        ret, frame = cap.read()

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # cv2.imshow("gray", gray)

        fgmask = fgbg.apply(gray)
        # cv2.imshow("fgmask", fgmask)

        retval, th = cv2.threshold(fgmask, 200, 255, cv2.THRESH_BINARY)
        # cv2.imshow("th", th)

        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))

        opening = cv2.morphologyEx(th, cv2.MORPH_OPEN, kernel, iterations=2)
        # cv2.imshow("opening", opening)

        dilation = cv2.dilate(opening, kernel, iterations=8)
        # cv2.imshow("dilation", dilation)

        closing = cv2.morphologyEx(dilation, cv2.MORPH_CLOSE, kernel, iterations=8)
        #
        # cv2.imshow("closing", closing)

        cv2.line(frame, xy1, xy2, (255, 0, 0), 3)

        cv2.line(frame, (xy1[0], posL - offset), (xy2[0], posL - offset), (255, 255, 0), 2)

        cv2.line(frame, (xy1[0], posL + offset), (xy2[0], posL + offset), (255, 255, 0), 2)

        contours, hierarchy = cv2.findContours(dilation, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        i = 0
        for cnt in contours:
            (x, y, w, h) = cv2.boundingRect(cnt)

            area = cv2.contourArea(cnt)

            if int(area) > 3000:
                centro = center(x, y, w, h)

                cv2.putText(frame, str(i), (x + 5, y + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)
                cv2.circle(frame, centro, 4, (0, 0, 255), -1)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                if len(detects) <= i:
                    detects.append([])
                if centro[1] > posL - offset and centro[1] < posL + offset:
                    detects[i].append(centro)
                else:
                    detects[i].clear()
                i += 1

        if i == 0:
            detects.clear()

        i = 0

        if len(contours) == 0:
            detects.clear()

        else:

            for detect in detects:
                for (c, l) in enumerate(detect):

                    if detect[c - 1][1] < posL and l[1] > posL:
                        detect.clear()
                        up += 1
                        total += 1
                        cv2.line(frame, xy1, xy2, (0, 255, 0), 5)
                        continue

                    if detect[c - 1][1] > posL and l[1] < posL:
                        detect.clear()
                        down += 1
                        total += 1
                        cv2.line(frame, xy1, xy2, (0, 0, 255), 5)
                        continue

                    if c > 0:
                        cv2.line(frame, detect[c - 1], l, (0, 0, 255), 1)

        cv2.putText(frame, "Total de Pessoas: " + str(total), (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
        cv2.putText(frame, "Entraram: " + str(up), (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
        cv2.putText(frame, "Sairam: " + str(down), (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)

        cv2.imshow("Analisando Movimento", frame)

        if cv2.waitKey(30) & 0xFF == ord('q'):
            break

    print("Total de Pessoas: " + str(total))

    cap.release()
    cv2.destroyAllWindows()
