package cat.uab.giantplayadmin.util;

import android.net.ConnectivityManager;
import android.net.DhcpInfo;
import android.net.NetworkInfo;
import android.net.wifi.WifiInfo;
import android.net.wifi.WifiManager;
import android.os.AsyncTask;
import android.util.Log;

import java.io.IOException;
import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import java.math.BigInteger;
import java.net.DatagramPacket;
import java.net.DatagramSocket;
import java.net.InetAddress;
import java.net.InterfaceAddress;
import java.net.NetworkInterface;
import java.net.SocketException;
import java.net.UnknownHostException;
import java.util.Enumeration;

public class UDPConnectTask extends AsyncTask<Void, Void, InetAddress> {

    public static final int UDPPORT = 6699;
    private static final String MESSAGE = "giantplay";
    /*public static InetAddress UDPHOST;

    static{
        try {
            UDPHOST = InetAddress.getByName("255.255.255.255");
        } catch (UnknownHostException e) {
            e.printStackTrace();
        }
    }*/

    private final ConnectTastListener context;
    private final WifiManager wifiManager;
    private final NetworkInfo networkInfo;

    public UDPConnectTask(ConnectTastListener context, WifiManager wifiManager, NetworkInfo networkInfo){
        this.context = context;
        this.wifiManager = wifiManager;
        this.networkInfo = networkInfo;
    }

    @Override
    protected void onPreExecute() {
        context.onPreFind();
    }

    @Override
    protected void onPostExecute(InetAddress address) {
        if(address == null)
            context.onNotFind();
    }

    public int getIpAddress() {
        int ipAddress = 0;
        WifiInfo wifiInfo = wifiManager.getConnectionInfo();
        if (wifiInfo == null || wifiInfo.equals("")) {
            return ipAddress;
        } else {
            ipAddress = wifiInfo.getIpAddress();
        }
        return ipAddress;
    }

    public static int getCodecIpAddress(WifiManager wm, NetworkInfo wifi){
        WifiInfo wi = wm.getConnectionInfo();
        if(wifi.isConnected())
            return wi.getIpAddress(); //normal wifi
        Method method = null;
        try {
            method = wm.getClass().getDeclaredMethod("getWifiApState");
        } catch (NoSuchMethodException e) {
            // TODO Auto-generated catch block
            e.printStackTrace();
        }
        if(method != null)
            method.setAccessible(true);
        int actualState = -1;
        try {
            if(method!=null)
                actualState = (Integer) method.invoke(wm, (Object[]) null);
        } catch (IllegalArgumentException e) {
            e.printStackTrace();
        } catch (IllegalAccessException e) {
            e.printStackTrace();
        } catch (InvocationTargetException e) {
            e.printStackTrace();
        }
        if(actualState==13){  //if wifiAP is enabled
            try {
                return ipToInt(InetAddress.getByName("192.168.43.1")); //hardcoded WifiAP ip
            } catch (UnknownHostException e) {
                e.printStackTrace();
            }
        }
        return 0;
    }

    public static int ipToInt(InetAddress ipAddr)
    {
        int compacted = 0;
        byte[] bytes = ipAddr.getAddress();
        for (int i=0 ; i<bytes.length ; i++) {
            compacted += (bytes[i] * Math.pow(256,4-i-1));
        }
        return compacted;
    }

    public static int convertIP2Int(byte[] ipAddress){
        return (int) (Math.pow(256, 3)*Integer.valueOf(ipAddress[3] & 0xFF)+Math.pow(256, 2)*Integer.valueOf(ipAddress[2] & 0xFF)+256*Integer.valueOf(ipAddress[1] & 0xFF)+Integer.valueOf(ipAddress[0] & 0xFF));
    }

    private InetAddress getBroadcastAddress(WifiManager wm, int ipAddress) throws IOException {
        DhcpInfo dhcp = wm.getDhcpInfo();
        if(dhcp == null)
            return InetAddress.getByName("255.255.255.255");
        int broadcast = (ipAddress & dhcp.netmask) | ~dhcp.netmask;
        byte[] quads = BigInteger.valueOf(broadcast).toByteArray();
        return InetAddress.getByAddress(quads);
    }

    public static String getBroadcast() throws SocketException {
        System.setProperty("java.net.preferIPv4Stack", "true");
        for (Enumeration<NetworkInterface> niEnum = NetworkInterface.getNetworkInterfaces(); niEnum.hasMoreElements();) {
            NetworkInterface ni = niEnum.nextElement();
            if (!ni.isLoopback()) {
                for (InterfaceAddress interfaceAddress : ni.getInterfaceAddresses()) {
                    return interfaceAddress.getBroadcast().toString().substring(1);
                }
            }
        }
        return null;
    }

    private InetAddress getBroadcastAddress() throws IOException {
        DhcpInfo dhcp = wifiManager.getDhcpInfo();
        // handle null somehow

        int broadcast = (dhcp.ipAddress & dhcp.netmask) | ~dhcp.netmask;
        byte[] quads = new byte[4];
        for (int k = 0; k < 4; k++)
            quads[k] = (byte) (broadcast >> (k * 8));
        return InetAddress.getByAddress(quads);
    }

    /**
     * Get network status
     *
     * @return Network status
     */
    public int getNetworkType() {
        return networkInfo == null ? -1 : networkInfo.getType();
    }

    public String getIp() {
        int networkType = getNetworkType();
        if (networkType == ConnectivityManager.TYPE_WIFI) {
            WifiInfo wifiInfo = wifiManager.getConnectionInfo();
            int ipAddress = wifiInfo.getIpAddress();
            return (ipAddress & 0xFF) + "." +
                    ((ipAddress >> 8) & 0xFF) + "." +
                    ((ipAddress >> 16) & 0xFF) + "." +
                    (ipAddress >> 24 & 0xFF);
        } else {
            try {
                for (Enumeration<NetworkInterface> en = NetworkInterface.getNetworkInterfaces(); en.hasMoreElements(); ) {
                    NetworkInterface intf = en.nextElement();
                    for (Enumeration<InetAddress> enumIpAddr = intf.getInetAddresses(); enumIpAddr.hasMoreElements(); ) {
                        InetAddress inetAddress = enumIpAddr.nextElement();
                        if (!inetAddress.isLoopbackAddress()) {
                            return inetAddress.getHostAddress();
                        }
                    }
                }
            } catch (SocketException e) {
                e.printStackTrace();
            }
            return null;
        }

    }

    @Override
    protected InetAddress doInBackground(Void... voids) {

        byte[] sendBuffer = MESSAGE.getBytes();
        byte[] recieveBuffer = new byte[MESSAGE.length()];

        try {

            //int ip = ipToInt(InetAddress.getByName(getIp()));//(wifiManager, networkInfo);

            //InetAddress broadcast = getBroadcastAddress(wifiManager, ip);

            //String bb = getBroadcast();

            InetAddress broadcast = getBroadcastAddress();

            DatagramSocket socket = new DatagramSocket();
            socket.setBroadcast(true);

            DatagramPacket packet
                    = new DatagramPacket(sendBuffer, sendBuffer.length, broadcast, UDPPORT);
            socket.send(packet);

            Log.d("UDPConnectTask", "Packet sent: " + packet);

            DatagramPacket recvPacket = new DatagramPacket(recieveBuffer, recieveBuffer.length);

            socket.setSoTimeout(1000);
            socket.receive(recvPacket);

            Log.d("UDPConnectTask", "Packet recieved: " + recvPacket);

            if(new String(recieveBuffer).equals(MESSAGE)){

                InetAddress address = recvPacket.getAddress();

                socket.close();

                context.onFind(address, UDPPORT);

                return address;

            }

        } catch (SocketException e) {
            e.printStackTrace();
        } catch (UnknownHostException e) {
            e.printStackTrace();
        } catch (IOException e) {
            e.printStackTrace();
        } catch (Exception e) {
            e.printStackTrace();
        }


        return null;
    }
}
