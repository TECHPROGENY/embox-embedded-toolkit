#include <QString>
#include <QCoreApplication>
#include <QDir>
#include <QDialog>
#include <QComboBox>
#include <QHBoxLayout>
#include <QVBoxLayout>
#include <QPushButton>
#include <QLabel>
#include <QTextEdit>
#include <QTextBrowser>
#include <QTextCursor>
#include <QString>
#include <QMetaObject>
#include <QMetaMethod>
#include <QLoggingCategory>


QString resourcePath(const QString& relativePath) {
    QString basePath = QCoreApplication::applicationDirPath();
    return QDir(basePath).absoluteFilePath(relativePath);
}


class SerialPopupWindow : public QDialog {
    Q_OBJECT

public:
    SerialPopupWindow(QWidget *parent = nullptr) : QDialog(parent) {
        setWindowTitle("Settings");

        serial_parity_combo = new QComboBox();
        serial_parity_combo->addItems({"NONE", "EVEN", "ODD", "SPACE", "MARK"});

        QHBoxLayout *parity_layout = new QHBoxLayout();
        QLabel *parity_label = new QLabel("Parity");
        parity_label->setStyleSheet("color: cyan");
        parity_layout->addWidget(parity_label);
        parity_layout->addWidget(serial_parity_combo);

        serial_stopbits_combo = new QComboBox();
        serial_stopbits_combo->addItems({"1", "1.5", "2"});

        QHBoxLayout *stopbits_layout = new QHBoxLayout();
        QLabel *stopbits_label = new QLabel("Stop bits");
        stopbits_label->setStyleSheet("color: cyan");
        stopbits_layout->addWidget(stopbits_label);
        stopbits_layout->addWidget(serial_stopbits_combo);

        serial_bytesize_combo = new QComboBox();
        serial_bytesize_combo->addItems({"5", "6", "7", "8"});

        QHBoxLayout *bytesize_layout = new QHBoxLayout();
        QLabel *bytesize_label = new QLabel("Byte size");
        bytesize_label->setStyleSheet("color: cyan");
        bytesize_layout->addWidget(bytesize_label);
        bytesize_layout->addWidget(serial_bytesize_combo);

        QPushButton *ok_button = new QPushButton("OK", this);
        connect(ok_button, &QPushButton::clicked, this, &SerialPopupWindow::accept);

        QPushButton *cancel_button = new QPushButton("Cancel", this);
        connect(cancel_button, &QPushButton::clicked, this, &SerialPopupWindow::reject);

        QHBoxLayout *buttons_layout = new QHBoxLayout();
        buttons_layout->addWidget(ok_button);
        buttons_layout->addWidget(cancel_button);

        QVBoxLayout *main_layout = new QVBoxLayout();
        main_layout->addLayout(parity_layout);
        main_layout->addLayout(stopbits_layout);
        main_layout->addLayout(bytesize_layout);
        main_layout->addLayout(buttons_layout);

        setLayout(main_layout);
    }

    QString getParity() const {
        return serial_parity_combo->currentText();
    }

    QString getStopBits() const {
        return serial_stopbits_combo->currentText();
    }

    QString getByteSize() const {
        return serial_bytesize_combo->currentText();
    }

private:
    QComboBox *serial_parity_combo;
    QComboBox *serial_stopbits_combo;
    QComboBox *serial_bytesize_combo;
};



class QTextEditHandler : public QObject, public QLoggingCategory {
    Q_OBJECT

public:
    QTextEditHandler(QTextEdit *serial_console) : QObject(), server_console(serial_console) {
        qRegisterMetaType<QLoggingCategory>("QLoggingCategory");
    }

public slots:
    void emitLog(const QLoggingCategory &category, const QString &msg) {
        Q_UNUSED(category);

        QTextCursor cursor = server_console->textCursor();
        cursor.movePosition(QTextCursor::End);
        cursor.insertText(msg);
        server_console->setTextCursor(cursor);
        server_console->ensureCursorVisible();
    }

private:
    QTextEdit *server_console;
};

#include <QMainWindow>
#include <QWidget>
#include <QHBoxLayout>
#include <QGroupBox>
#include <QFormLayout>
#include <QPushButton>
#include <QIcon>
#include <QLabel>
#include <QStackedWidget>

class MainWindow : public QMainWindow {
    Q_OBJECT

public:
    MainWindow(QWidget *parent = nullptr) : QMainWindow(parent) {
        central_widget = new QWidget();
        setCentralWidget(central_widget);

        main_layout = new QHBoxLayout();

        left_bar_group = new QGroupBox();
        left_bar_group_layout = new QFormLayout();
        left_bar_group->setLayout(left_bar_group_layout);

        server_button = new QPushButton();
        server_button->setFixedSize(80, 70);
        server_icon = QIcon(resourcePath("server2.png"));
        server_button->setIcon(server_icon);
        server_button->setIconSize(QSize(80, 70));
        server_button->setObjectName("serverButton");

        client_button = new QPushButton();
        client_icon = QIcon(resourcePath("client.png"));
        client_button->setIcon(client_icon);
        client_button->setFixedSize(80, 70);
        client_button->setIconSize(QSize(80, 70));
        client_button->setObjectName("clientButton");

        serial_button = new QPushButton();
        serial_icon = QIcon(resourcePath("db89.png"));
        serial_button->setIcon(serial_icon);
        serial_button->setFixedSize(80, 70);
        serial_button->setIconSize(QSize(80, 70));
        serial_button->setObjectName("serialButton");

        left_bar_group_layout->addRow(server_button);
        left_bar_group_layout->addRow(new QLabel(""));
        left_bar_group_layout->addRow(client_button);
        left_bar_group_layout->addRow(new QLabel(""));
        left_bar_group_layout->addRow(serial_button);
        left_bar_group_layout->addRow(new QLabel(""));

        right_text = new QLabel("This is the default text.");

        main_console = nullptr;
        serverConf();
        serialConf();
        client_conf();

        stacked_widget = new QStackedWidget();

        server_widget = new QLabel("Server Widget");
        client_widget = new QLabel("Client Widget");
        serial_widget = new QLabel("Serial Widget");
        network_widget = new QLabel("Network Widget");
        security_widget = new QLabel("Security Widget");
        about_widget = new QLabel("About Widget");

        stacked_widget->addWidget(server_form_widget);
        stacked_widget->addWidget(client_form_widget);
        stacked_widget->addWidget(serial_form_widget);
        stacked_widget->addWidget(network_widget);
        stacked_widget->addWidget(security_widget);
        stacked_widget->addWidget(about_widget);

        main_layout->addWidget(left_bar_group);
        main_layout->addWidget(stacked_widget);

        central_widget->setLayout(main_layout);

        connect(server_button, &QPushButton::clicked, this, &MainWindow::on_serverButton_clicked);
        connect(client_button, &QPushButton::clicked, this, &MainWindow::on_clientButton_clicked);
        connect(serial_button, &QPushButton::clicked, this, &MainWindow::on_serialButton_clicked);

        setWindowTitle("MBOX v0.1 Beta");
        setGeometry(100, 100, 1000, 600);
        show();
    }

private:
    QWidget *central_widget;
    QHBoxLayout *main_layout;
    QGroupBox *left_bar_group;
    QFormLayout *left_bar_group_layout;
    QPushButton *server_button;
    QIcon server_icon;
    QPushButton *client_button;
    QIcon client_icon;
    QPushButton *serial_button;
    QIcon serial_icon;
    QLabel *right_text;
    QTextEdit *main_console;
    QStackedWidget *stacked_widget;
        // ...

    QWidget *server_form_widget;
    QWidget *client_form_widget;
    QWidget *serial_form_widget;
    QWidget *network_widget;
    QWidget *security_widget;
    QWidget *about_widget;

    void serverConf() {
        server_form_widget = new QWidget();
        // Add server configuration widgets to server_form_widget
        // ...

        // Example: Adding a label
        QLabel *server_label = new QLabel("Server Configuration");
        QVBoxLayout *server_layout = new QVBoxLayout(server_form_widget);
        server_layout->addWidget(server_label);
        // ...

        stacked_widget->addWidget(server_form_widget);
    }

    void client_conf() {
        client_form_widget = new QWidget();
        // Add client configuration widgets to client_form_widget
        // ...

        stacked_widget->addWidget(client_form_widget);
    }

    void serialConf() {
        serial_form_widget = new QWidget();
        // Add serial configuration widgets to serial_form_widget
        // ...

        stacked_widget->addWidget(serial_form_widget);
    }

public slots:
    void on_serverButton_clicked() {
        stacked_widget->setCurrentWidget(server_form_widget);
    }

    void on_clientButton_clicked() {
        stacked_widget->setCurrentWidget(client_form_widget);
    }

    void on_serialButton_clicked() {
        stacked_widget->setCurrentWidget(serial_form_widget);
    }

    // ...
};
