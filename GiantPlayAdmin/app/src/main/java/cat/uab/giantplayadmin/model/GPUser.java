package cat.uab.giantplayadmin.model;

public interface GPUser {

    String getKey();

    String getName();

    int getDelay();
    void setDelay(int d);

    GPParams getParams();
    void setParams(GPParams params);

    void sendEvent(String key, double... values);
    void sendEvent(String key, float... values);

    void logout();

}
