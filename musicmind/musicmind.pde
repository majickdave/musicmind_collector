
JSONArray lyricsData;

PFont font;

Song[] songs;

Song track;

void setup() {
  size(1000, 1000, P3D);
  noStroke();
  ortho();
  
  background(0);
  
  font = createFont("Carlito-Regular", 23);
  // load JSON data
  lyricsData =loadJSONArray("lyrics.json");
  // size arrays
  int dataSize = lyricsData.size();
  
  songs = new Song[dataSize];

  for (int i=0; i<dataSize; i++) {
    
    JSONObject song = lyricsData.getJSONObject(i);
    //try {
    JSONArray lyrics = song.getJSONArray("lyrics");
    //  String words = song.getString("lyrics");
    
    //  print(s);
    //} catch (IOException e) {
    //e.printStackTrace();
    //line = null;
    //} if(words != null) {
      print(lyrics);
      fill(85);
      
      JSONArray words = lyrics.getJSONArray(0);
      
      for (int j=0; j< lyrics.size(); j++) {
        
        String s = words.getString(j);
        float w = textWidth(s);
        textFont(font, 12+j);
        text(s, (width-w)/2, 25);
        
      }
    }
    words[i] = new Song(new PVector(width/2, height/2-25), song
  }
  
  void draw() {


    
  }
 