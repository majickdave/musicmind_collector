class Song {
  
 PVector loc;
 float size;
 float duration;
 String lyrics;
 
 Song() {
   
 }
 
 Song(PVector loc, float size, float duration, String lyrics) {
  this.loc = loc;
  this.size = size;
  this.duration = duration;
  this.lyrics = lyrics;
 }
 
 void display() {
  pushMatrix();
  translate(loc.x, loc.y, loc.z);
  text(lyrics, loc.x, loc.y);
  popMatrix();
 }
 
 Boolean isHit() {
  if (dist(mouseX, mouseY, loc.x, loc.y) < size) {
    return true;
  }
  return false;
 }
 
 //void resetCol(){
 //  col = origCol;
 //}
  
}