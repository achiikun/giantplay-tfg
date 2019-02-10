package cat.uab.giantplayadmin.util;

import java.net.InetAddress;

import cat.uab.giantplayadmin.model.GPConnection;

public interface ConnectTastListener {
    void onPreFind();

    void onFind(InetAddress address, int port);

    void onNotFind();
}
