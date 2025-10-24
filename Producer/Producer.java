package Producer;

import java.util.ArrayList;
import java.util.Random;

public class Producer {
    private int positionX;
    private int positionY;
    private int speedX;
    private int speedY;

    private void GetPosition(){
        Random rand = new Random();
        positionX = rand.nextInt(100);
        positionY = rand.nextInt(100);
    }

    private void GetSpeed(){
        Random rand = new Random();
        speedX = rand.nextInt(100);
        speedY = rand.nextInt(100);
    }
    private ArrayList<Integer> GetData(){
        ArrayList<Integer> data = new ArrayList<>();
        GetPosition();
        GetSpeed();
        data.add(positionX);
        data.add(positionY);
        data.add(speedX);
        data.add(speedY);
        return data;
    }
}
