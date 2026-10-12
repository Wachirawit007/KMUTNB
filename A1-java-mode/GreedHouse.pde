import java.io.File;
import java.util.ArrayList;
import java.util.HashMap;

final int GAME_FPS = 60;
final String MENU = "MENU";
final String FARM = "FARM";
final String BONUS_FARM = "BONUS_FARM";
final String SHOP = "SHOP";
final String PLAYING = "PLAYING";
final String STOPPED = "STOPPED";
final String COLLAPSED = "COLLAPSED";
final String STATISTICS = "STATISTICS";

final String[] MATERIALS = {"WOOD", "BRICK", "IRON", "GOLD", "DIAMOND"};
final int[] MATERIAL_COSTS = {0, 5, 15, 25, 50};
final float[] RISK_MULTIPLIERS = {1.0, 0.70, 0.45, 0.30, 0.0};
final int[] MATERIAL_COLORS = new int[5];
final String[] FARM_MATERIALS = {"BRICK", "IRON", "GOLD", "DIAMOND"};
final int[] FARM_WEIGHTS = {50, 30, 15, 5};
final float[][] FARM_SPEEDS = {{5.0, 7.0}, {6.5, 9.0}, {8.5, 11.5}, {11.0, 15.0}};

int colorMenu, colorPlay, colorFarm, colorGround, colorDamaged, colorRoof;
int colorWindow, colorDoor, colorOutline, colorDanger, colorSafe, colorWarning;
int colorCoin, colorText, colorLight, colorCrack, colorButton, colorButtonBorder;
int colorBuild, colorStop, colorSelected;

PFont fontSmall, fontMedium, fontLarge, fontTitle;
String currentState = MENU;
String selectedMaterial = "WOOD";
int currentFloor = 0;
int bestFloor = 0;
int coins = 100;
final int STARTER_COINS = 100;
int[] inventory = new int[5];
boolean shopFromPlaying = false;

ArrayList<Crack> cracks = new ArrayList<Crack>();
ArrayList<Integer> floorMaterials = new ArrayList<Integer>();
ArrayList<FallingItem> farmItems = new ArrayList<FallingItem>();
HashMap<String, HitBox> buttons = new HashMap<String, HitBox>();

String shopMessage = "";
int shopMessageTimer = 0;
int shopMessageColor;
boolean closeCallActive = false;
int closeCallTimer = 0;
String milestoneMessage = "";
int milestoneTimer = 0;
String centerMessage = "";
int centerMessageTimer = 0;
boolean milestone50Awarded = false;
int farmTimeLeft = 0;
int farmSpawnCooldown = 0;

int lastRoundFloor = 0;
String lastRoundResult = "";
String lastRoundMaterial = "WOOD";
int greedScore = 0;
String greedLabel = "";

int statHighestAttempt = 0;
int statTotalAttempts = 0;
int statTotalCollapses = 0;
int statTotalStops = 0;
int statTotalFloorsBuilt = 0;
int statTotalCoinsEarned = 0;
String saveFile;

void settings() {
  size(1280, 720);
}

void setup() {
  surface.setTitle("GREED HOUSE");
  surface.setResizable(true);
  frameRate(GAME_FPS);
  textAlign(CENTER, CENTER);
  rectMode(CORNER);

  fontSmall = createFont("Arial", 20, false);
  fontMedium = createFont("Arial", 28, false);
  fontLarge = createFont("Arial", 48, false);
  fontTitle = createFont("Arial", 64, true);

  colorMenu = color(245, 240, 222);
  colorPlay = color(198, 226, 250);
  colorFarm = color(210, 240, 210);
  colorGround = color(150, 200, 140);
  colorDamaged = color(200, 150, 120);
  colorRoof = color(200, 70, 40);
  colorWindow = color(120, 190, 230);
  colorDoor = color(90, 55, 30);
  colorOutline = color(35, 22, 15);
  colorDanger = color(200, 30, 30);
  colorSafe = color(40, 140, 70);
  colorWarning = color(230, 160, 20);
  colorCoin = color(235, 190, 50);
  colorText = color(40, 40, 40);
  colorLight = color(255);
  colorCrack = color(70, 60, 55);
  colorButton = color(250);
  colorButtonBorder = color(15);
  colorBuild = color(200, 230, 200);
  colorStop = color(240, 200, 200);
  colorSelected = color(255, 245, 200);
  MATERIAL_COLORS[0] = color(196, 154, 108);
  MATERIAL_COLORS[1] = color(188, 92, 70);
  MATERIAL_COLORS[2] = color(150, 155, 165);
  MATERIAL_COLORS[3] = color(232, 189, 60);
  MATERIAL_COLORS[4] = color(185, 235, 250);

  saveFile = new File(sketchPath("../greed_house_save.json")).getAbsolutePath();
  shopMessageColor = colorDanger;
  loadData();
}

void draw() {
  updateGame();
  buttons.clear();
  if (currentState.equals(MENU)) showMainMenu();
  else if (currentState.equals(FARM)) showFarm(false);
  else if (currentState.equals(BONUS_FARM)) showFarm(true);
  else if (currentState.equals(SHOP)) showShop();
  else if (currentState.equals(PLAYING)) showPlaying();
  else if (currentState.equals(STOPPED)) showStopped();
  else if (currentState.equals(COLLAPSED)) showCollapsed();
  else if (currentState.equals(STATISTICS)) showStatistics();
}

void mousePressed() {
  if (currentState.equals(MENU)) {
    if (hit("build_house")) enterFarm();
    else if (hit("statistics")) currentState = STATISTICS;
    else if (hit("quit")) {
      saveData();
      exit();
    }
  } else if (currentState.equals(FARM) || currentState.equals(BONUS_FARM)) {
    collectItemAt(mouseX, mouseY);
  } else if (currentState.equals(SHOP)) {
    if (hit("build_btn")) {
      if (shopFromPlaying) currentState = PLAYING;
      else {
        resetGame();
        currentState = PLAYING;
      }
    } else {
      for (String material : MATERIALS) {
        String key = material.toLowerCase();
        if (!material.equals("WOOD") && hit(key + "_buy_btn")) {
          buyMaterial(material);
          break;
        }
        if (hit(key + "_card")) {
          selectMaterial(material);
          break;
        }
      }
    }
  } else if (currentState.equals(PLAYING)) {
    if (hit("build")) buildHigher();
    else if (hit("stop")) stopGame();
    else if (hit("shop_mid_build")) enterShopFromPlaying();
    else {
      for (String material : MATERIALS) {
        if (hit("mat_" + material.toLowerCase())) {
          selectMaterial(material);
          break;
        }
      }
    }
  } else if (currentState.equals(STOPPED)) {
    if (hit("play_again")) enterFarm();
    else if (hit("main_menu")) currentState = MENU;
  } else if (currentState.equals(COLLAPSED)) {
    if (hit("try_again")) {
      clearBrokenHouse();
      enterFarm();
    }
  } else if (currentState.equals(STATISTICS) && hit("back")) {
    currentState = MENU;
  }
}

void keyPressed() {
  if (currentState.equals(PLAYING)) {
    if (key == ' ') buildHigher();
    else if (keyCode == ENTER || keyCode == RETURN) stopGame();
    else if (key == 's' || key == 'S') enterShopFromPlaying();
  }
}

void drawBackground(int c) {
  background(c);
}

void drawText(String value, float x, float y, PFont font, int c) {
  fill(c);
  textFont(font);
  text(value, x, y);
}

void drawTextCenter(String value, float y, PFont font, int c) {
  drawText(value, width / 2.0, y, font, c);
}

void drawButton(String id, float x, float y, float w, float h, String label, int fillColor, PFont font) {
  buttons.put(id, new HitBox(x, y, w, h));
  stroke(colorButtonBorder);
  strokeWeight(5);
  fill(fillColor);
  rect(x, y, w, h, 8);
  noStroke();
  drawText(label, x + w / 2, y + h / 2, font, colorText);
}

boolean hit(String id) {
  HitBox box = buttons.get(id);
  return box != null && box.contains(mouseX, mouseY);
}

void drawRoof(float x, float y, float w, int c) {
  float roofHeight = w * 0.35;
  fill(c);
  stroke(colorOutline);
  strokeWeight(2);
  triangle(x + w / 2, y - roofHeight, x, y, x + w, y);
}

void drawHouse(int floors, float areaTop, float areaBottom, float centerX, ArrayList<Integer> colors, int defaultColor) {
  float floorWidth = 200;
  float floorHeight = 46;
  float roofExtra = floorWidth * 0.35;
  float totalHeight = floors * floorHeight + roofExtra;
  float availableHeight = areaBottom - areaTop;
  float scale = totalHeight > availableHeight ? availableHeight / totalHeight : 1.0;
  scale = max(scale, 0.12);
  float scaledWidth = floorWidth * scale;
  float scaledHeight = floorHeight * scale;
  float baseX = centerX - scaledWidth / 2;
  float baseY = areaBottom;

  for (int i = 0; i < floors; i++) {
    float x = baseX + tiltOffset(i, floors);
    float y = baseY - (i + 1) * scaledHeight;
    int wallColor = i < colors.size() ? colors.get(i) : defaultColor;
    if (floors >= 11) wallColor = colorDamaged;
    stroke(colorOutline);
    strokeWeight(2);
    fill(wallColor);
    rect(x, y, scaledWidth, scaledHeight);
    strokeWeight(4);
    line(x, y, x + scaledWidth, y);
    line(x, y + scaledHeight - 2, x + scaledWidth, y + scaledHeight - 2);

    float windowSize = max(10, 16 * scale);
    drawWindow(x + scaledWidth / 2 - windowSize / 2, y + scaledHeight / 2 - windowSize / 2, windowSize);
    if (i == 0) {
      float doorW = max(10, 26 * scale);
      float doorH = max(14, 38 * scale);
      drawDoor(x + scaledWidth / 2 - doorW / 2, y + scaledHeight - doorH, doorW, doorH);
    }
  }

  float roofX = baseX + tiltOffset(floors, floors);
  float roofY = baseY - floors * scaledHeight;
  drawRoof(roofX, roofY, scaledWidth, colorRoof);
  drawHouseDamage(floors, baseX, baseY, floorWidth, floorHeight, scale);
}

float tiltOffset(int floorIndex, int floors) {
  if (floors <= 5) return 0;
  float strength = min((floors - 5) * 0.6, 18);
  return (float) floorIndex / max(floors, 1) * strength;
}

void drawWindow(float x, float y, float size) {
  stroke(colorOutline);
  strokeWeight(2);
  fill(colorWindow);
  rect(x, y, size, size);
  strokeWeight(1);
  line(x + size / 2, y, x + size / 2, y + size);
  line(x, y + size / 2, x + size, y + size / 2);
}

void drawDoor(float x, float y, float w, float h) {
  stroke(colorOutline);
  strokeWeight(2);
  fill(colorDoor);
  rect(x, y, w, h);
  noStroke();
  fill(230, 220, 180);
  ellipse(x + w - 6, y + h / 2, 4, 4);
}

void drawHouseDamage(int floors, float baseX, float baseY, float floorWidth, float floorHeight, float scale) {
  if (floors >= 16) {
    float topY = baseY - floors * floorHeight * scale - 40 * scale;
    drawText("!", baseX + floorWidth * scale / 2 - 5, topY, fontMedium, colorWarning);
  }
  stroke(colorCrack);
  strokeWeight(2);
  for (Crack crack : cracks) {
    float y = baseY - crack.floorIndex * floorHeight * scale;
    float x = baseX + crack.offsetX * scale + tiltOffset(crack.floorIndex, floors);
    float crackY = y - crack.offsetY * scale;
    line(x, crackY, x + 8 * scale, crackY + 10 * scale);
    line(x + 8 * scale, crackY + 10 * scale, x - 4 * scale, crackY + 20 * scale);
  }
}

void drawUi() {
  drawTextCenter("GREED HOUSE", 40, fontLarge, colorText);
  drawTextCenter("EVERY 20 FLOORS: +125 COINS   |   EVERY 50 FLOORS: BONUS FIND RESOURCES", 75, fontSmall, colorText);
  textAlign(LEFT, CENTER);
  text("CURRENT FLOOR: " + currentFloor, 30, 100);
  text("BEST: " + bestFloor, 30, 130);
  text("MATERIAL: " + selectedMaterial, 30, 160);
  text("COINS: " + coins, 30, 185);
  textAlign(CENTER, CENTER);

  int sideX = width - 260;
  int sideY = 100;
  if (milestoneTimer > 0 && !milestoneMessage.equals("")) {
    drawPanel(sideX - 10, sideY - 10, 250, 50, colorWarning);
    drawText(milestoneMessage, sideX + 115, sideY + 15, fontSmall, colorWarning);
    sideY += 60;
  }
  if (closeCallActive) {
    drawPanel(sideX - 10, sideY - 10, 250, 50, colorDanger);
    drawText("⚠ CLOSE CALL", sideX + 115, sideY + 15, fontSmall, colorDanger);
  }
}

void drawPanel(float x, float y, float w, float h, int border) {
  stroke(border);
  strokeWeight(4);
  fill(colorButton);
  rect(x, y, w, h, 8);
  noStroke();
}

void drawCenterMessage() {
  if (centerMessageTimer <= 0 || centerMessage.equals("")) return;
  float panelWidth = min(width - 80, 700);
  drawPanel((width - panelWidth) / 2, height / 2 - 40, panelWidth, 80, colorWarning);
  drawTextCenter(centerMessage, height / 2, fontMedium, colorDanger);
}

void drawMaterialSelector() {
  float x = 30;
  float y = 235;
  float w = 95;
  float h = 55;
  for (String material : MATERIALS) {
    boolean chosen = selectedMaterial.equals(material);
    boolean available = material.equals("WOOD") || inventory[materialIndex(material)] > 0;
    int buttonColor = chosen ? colorSelected : (available ? colorButton : color(210));
    int border = chosen ? colorSafe : colorButtonBorder;
    stroke(border);
    strokeWeight(3);
    fill(buttonColor);
    rect(x, y, w, h, 6);
    noStroke();
    textAlign(LEFT, CENTER);
    drawText(material, x + 8, y + 15, fontSmall, colorText);
    String owned = material.equals("WOOD") ? "∞" : str(inventory[materialIndex(material)]);
    drawText("x" + owned, x + 8, y + 40, fontSmall, colorText);
    textAlign(CENTER, CENTER);
    buttons.put("mat_" + material.toLowerCase(), new HitBox(x, y, w, h));
    x += w + 10;
  }
}

void showMainMenu() {
  drawBackground(colorMenu);
  drawTextCenter("GREED HOUSE", 140, fontTitle, colorText);
  drawTextCenter("HOW HIGH CAN YOU GO?", 210, fontMedium, colorText);
  drawButton("build_house", width / 2 - 130, 290, 260, 60, "BUILD HOUSE", colorButton, fontMedium);
  drawButton("statistics", width / 2 - 130, 370, 260, 60, "STATISTICS", colorButton, fontMedium);
  drawButton("quit", width / 2 - 130, 450, 260, 60, "QUIT", colorButton, fontMedium);
}

void showFarm(boolean bonus) {
  drawBackground(colorFarm);
  drawTextCenter(bonus ? "BONUS FIND RESOURCES!" : "FIND RESOURCES", 60, fontLarge, bonus ? colorWarning : colorText);
  drawTextCenter("Click blocks to collect BRICK / IRON / GOLD / DIAMOND, or grab falling COINS", 105, fontSmall, colorText);
  drawTextCenter("TIME: " + max(0, farmTimeLeft / GAME_FPS + 1), 150, fontMedium, colorWarning);
  drawTextCenter(bonus ? "FLOOR: " + currentFloor + "   COINS: " + coins : "COINS: " + coins, 190, fontMedium, colorText);
  drawFarmInventory(220);

  for (FallingItem item : farmItems) {
    if (item.isCoin) {
      fill(colorCoin);
      stroke(colorOutline);
      strokeWeight(3);
      ellipse(item.x, item.y, item.size, item.size);
      drawText(str(item.value), item.x, item.y, fontSmall, colorOutline);
    } else {
      int idx = materialIndex(item.material);
      fill(MATERIAL_COLORS[idx]);
      stroke(colorOutline);
      strokeWeight(3);
      rect(item.x - item.size / 2, item.y - item.size / 2, item.size, item.size);
      drawText(item.material.substring(0, 1), item.x, item.y, fontSmall, colorOutline);
    }
  }
  if (bonus) drawCenterMessage();
}

void drawFarmInventory(float y) {
  drawTextCenter("OWNED - BRICK: " + inventory[1] + "   IRON: " + inventory[2] + "   GOLD: " + inventory[3] + "   DIAMOND: " + inventory[4], y, fontSmall, colorText);
}

void showShop() {
  drawBackground(colorMenu);
  drawTextCenter("STOCK UP ON MATERIALS", 80, fontLarge, colorText);
  drawTextCenter("COINS: " + coins, 125, fontMedium, colorWarning);
  drawTextCenter("Click a card to select it - click BUY to add to your stockpile", 152, fontSmall, colorText);
  if (shopMessageTimer > 0 && !shopMessage.equals("")) drawTextCenter(shopMessage, 175, fontSmall, shopMessageColor);

  String[][] descriptions = {
    {"FREE & UNLIMITED", "Normal risk"},
    {"COST 5 EACH", "Safer (-30% risk)"},
    {"COST 15 EACH", "Safer (-55% risk)"},
    {"COST 25 EACH", "Safer (-70% risk)"},
    {"COST 50 EACH", "Safest (-100% risk)"}
  };
  float cardW = 200;
  float cardH = 230;
  float gap = 20;
  float startX = width / 2.0 - (cardW * 5 + gap * 4) / 2;
  float top = 210;
  for (int i = 0; i < MATERIALS.length; i++) {
    String material = MATERIALS[i];
    float x = startX + i * (cardW + gap);
    boolean chosen = selectedMaterial.equals(material);
    boolean canSelect = i == 0 || inventory[i] > 0;
    boolean canAfford = i == 0 || coins >= MATERIAL_COSTS[i];
    stroke(chosen ? colorSafe : colorButtonBorder);
    strokeWeight(5);
    fill(chosen ? colorSelected : (!canSelect ? color(225) : colorButton));
    rect(x, top, cardW, cardH, 10);
    noStroke();
    fill(MATERIAL_COLORS[i]);
    stroke(colorOutline);
    strokeWeight(2);
    rect(x + cardW / 2 - 25, top + 13, 50, 50);
    noStroke();
    drawText(material, x + cardW / 2, top + 78, fontMedium, colorText);
    drawText(descriptions[i][0], x + cardW / 2, top + 112, fontSmall, colorText);
    drawText(descriptions[i][1], x + cardW / 2, top + 132, fontSmall, colorText);
    String owned = i == 0 ? "UNLIMITED" : "OWNED: " + inventory[i];
    drawText(owned, x + cardW / 2, top + 160, fontSmall, chosen ? colorSafe : colorText);
    buttons.put(material.toLowerCase() + "_card", new HitBox(x, top, cardW, cardH));
    if (i > 0) {
      int buyColor = canAfford ? colorBuild : color(200);
      drawButton(material.toLowerCase() + "_buy_btn", x + 35, top + cardH - 41, 130, 34, "BUY +1", buyColor, fontSmall);
    }
  }
  drawButton("build_btn", width / 2 - 130, top + cardH + 40, 260, 60,
    shopFromPlaying ? "BACK TO BUILDING" : "START BUILDING", colorBuild, fontMedium);
}

void showPlaying() {
  drawBackground(colorPlay);
  float groundY = height - 100;
  noStroke();
  fill(colorGround);
  rect(0, groundY, width, height - groundY);
  ArrayList<Integer> houseColors = new ArrayList<Integer>();
  for (int material : floorMaterials) houseColors.add(MATERIAL_COLORS[material]);
  drawHouse(currentFloor, 305, groundY, width / 2.0, houseColors, MATERIAL_COLORS[materialIndex(selectedMaterial)]);
  drawUi();
  drawMaterialSelector();
  drawCenterMessage();
  drawButton("build", width / 2.0 - 280, height - 80, 260, 60, "BUILD HIGHER", colorBuild, fontMedium);

  float stopX = width / 2.0 + 20;
  buttons.put("stop", new HitBox(stopX, height - 80, 260, 60));
  stroke(colorButtonBorder);
  strokeWeight(5);
  fill(colorStop);
  rect(stopX, height - 80, 260, 60, 8);
  drawText("STOP", stopX + 130, height - 56, fontMedium, colorText);
  drawText("(+Point 10)", stopX + 130, height - 32, fontSmall, colorText);
  drawButton("shop_mid_build", width - 170, 27, 140, 45, "SHOP", colorSelected, fontSmall);
}

void showResultScreen(String title, int titleColor, String[] lines, float yOffset, boolean drawBg) {
  if (drawBg) drawBackground(colorMenu);
  drawTextCenter(title, 120 + yOffset, fontLarge, titleColor);
  float y = 190 + yOffset;
  for (String lineText : lines) {
    drawTextCenter(lineText, y, fontMedium, colorText);
    y += 38;
  }
  if (currentState.equals(STOPPED)) {
    drawButton("play_again", width / 2.0 - 260, y + 12, 240, 55, "PLAY AGAIN", colorButton, fontMedium);
    drawButton("main_menu", width / 2.0 + 20, y + 12, 240, 55, "MAIN MENU", colorButton, fontMedium);
  } else {
    drawButton("try_again", width / 2.0 - 120, y + 12, 240, 55, "TRY AGAIN", colorButton, fontMedium);
  }
}

void showStopped() {
  showResultScreen("YOU STOPPED", colorSafe,
    new String[] {"YOU STOPPED", "FINAL FLOOR: " + lastRoundFloor, "SCORE: " + greedScore + " (" + greedLabel + ")", "( +10 Points)"}, 0, true);
}

void showCollapsed() {
  drawBackground(colorMenu);
  ArrayList<Integer> houseColors = new ArrayList<Integer>();
  for (int material : floorMaterials) houseColors.add(MATERIAL_COLORS[material]);
  drawHouse(lastRoundFloor, 20, 235, width / 2.0, houseColors, MATERIAL_COLORS[materialIndex(lastRoundMaterial)]);
  showResultScreen("THE HOUSE COLLAPSED", colorDanger,
    new String[] {"THE HOUSE COLLAPSED", "FINAL FLOOR: " + lastRoundFloor, "SCORE: " + greedScore + " (" + greedLabel + ")"}, 170, false);
}

void showStatistics() {
  drawBackground(colorMenu);
  drawTextCenter("STATISTICS", 100, fontLarge, colorText);
  String[] lines = {
    "BEST FLOOR       " + bestFloor,
    "TOTAL ATTEMPTS   " + statTotalAttempts,
    "COLLAPSES        " + statTotalCollapses,
    "STOPS            " + statTotalStops,
    "TOTAL FLOORS     " + statTotalFloorsBuilt,
    "COINS EARNED     " + statTotalCoinsEarned
  };
  float y = 200;
  for (String lineText : lines) {
    drawTextCenter(lineText, y, fontMedium, colorText);
    y += 45;
  }
  drawButton("back", width / 2.0 - 100, y + 12, 200, 55, "BACK", colorButton, fontMedium);
}

float calculateRisk(int floors) {
  float baseRisk = min(0.018 + floors * 0.007, 0.90);
  return min(baseRisk * RISK_MULTIPLIERS[materialIndex(selectedMaterial)], 0.90);
}

boolean checkCollapse(int floors) {
  return random(1) < calculateRisk(floors);
}

String milestoneFor(int floors) {
  if (floors == 5) return "You're doing fine.";
  if (floors == 10) return "Still going?";
  if (floors == 15) return "Are you sure?";
  if (floors == 20) return "One more?";
  if (floors == 25) return "You could stop now.";
  if (floors == 30 || (floors > 30 && floors % 5 == 0)) return "How high do you want to go?";
  return "";
}

void showShopMessage(String message, int c) {
  shopMessage = message;
  shopMessageColor = c;
  shopMessageTimer = GAME_FPS * 2;
}

void addCrack() {
  cracks.add(new Crack((int) random(max(currentFloor, 1)), (int) random(20, 161), (int) random(5, 36)));
}

void resetGame() {
  currentFloor = 0;
  cracks.clear();
  closeCallActive = false;
  closeCallTimer = 0;
  milestoneMessage = "";
  milestoneTimer = 0;
  floorMaterials.clear();
  milestone50Awarded = false;
  centerMessage = "";
  centerMessageTimer = 0;
}

void clearBrokenHouse() {
  cracks.clear();
  floorMaterials.clear();
}

void enterFarm() {
  coins = STARTER_COINS;
  for (int i = 1; i < inventory.length; i++) inventory[i] = 0;
  farmTimeLeft = 15 * GAME_FPS;
  farmItems.clear();
  farmSpawnCooldown = 0;
  currentState = FARM;
  saveData();
}

void triggerBonusFarm() {
  farmTimeLeft = 6 * GAME_FPS;
  farmItems.clear();
  farmSpawnCooldown = 0;
  currentState = BONUS_FARM;
}

void enterShop() {
  shopFromPlaying = false;
  currentState = SHOP;
}

void enterShopFromPlaying() {
  shopFromPlaying = true;
  currentState = SHOP;
}

void selectMaterial(String material) {
  if (material.equals("WOOD") || inventory[materialIndex(material)] > 0) selectedMaterial = material;
  else showShopMessage("YOU DON'T OWN ANY " + material + " YET", colorDanger);
}

void buyMaterial(String material) {
  int idx = materialIndex(material);
  if (idx == 0) return;
  if (coins < MATERIAL_COSTS[idx]) {
    showShopMessage("NOT ENOUGH COINS (NEED " + MATERIAL_COSTS[idx] + ")", colorDanger);
    return;
  }
  coins -= MATERIAL_COSTS[idx];
  inventory[idx]++;
  showShopMessage("BOUGHT 1 " + material + " (OWNED: " + inventory[idx] + ")", colorSafe);
  saveData();
}

void updateFarm() {
  farmTimeLeft--;
  if (farmTimeLeft <= 0) {
    if (currentState.equals(BONUS_FARM)) currentState = PLAYING;
    else enterShop();
    return;
  }
  farmSpawnCooldown--;
  if (farmSpawnCooldown <= 0) {
    if (random(1) < 0.3) {
      int value = (int) random(20, 41);
      float speed = 5.0 + (value - 20) / 20.0 * 11.0;
      farmItems.add(new FallingItem(random(60, width - 60), -20, speed, 30, true, "", value));
    } else {
      int selected = weightedMaterial();
      String material = FARM_MATERIALS[selected];
      float[] range = FARM_SPEEDS[selected];
      farmItems.add(new FallingItem(random(60, width - 60), -20, random(range[0], range[1]), 32, false, material, 0));
    }
    farmSpawnCooldown = (int) random(10, 23);
  }
  for (int i = farmItems.size() - 1; i >= 0; i--) {
    FallingItem item = farmItems.get(i);
    item.y += item.speed;
    if (item.y > height + 30) farmItems.remove(i);
  }
}

int weightedMaterial() {
  int roll = (int) random(100);
  int total = 0;
  for (int i = 0; i < FARM_WEIGHTS.length; i++) {
    total += FARM_WEIGHTS[i];
    if (roll < total) return i;
  }
  return FARM_WEIGHTS.length - 1;
}

void collectItemAt(float x, float y) {
  for (int i = 0; i < farmItems.size(); i++) {
    FallingItem item = farmItems.get(i);
    float half = item.size / 2.0 + 10;
    if (x >= item.x - half && x <= item.x + half && y >= item.y - half && y <= item.y + half) {
      farmItems.remove(i);
      if (item.isCoin) {
        coins += item.value;
        statTotalCoinsEarned += item.value;
      } else inventory[materialIndex(item.material)]++;
      break;
    }
  }
}

void buildHigher() {
  String used = selectedMaterial;
  currentFloor++;
  statTotalFloorsBuilt++;
  statHighestAttempt = max(statHighestAttempt, currentFloor);
  floorMaterials.add(materialIndex(used));
  if (!used.equals("WOOD")) {
    int idx = materialIndex(used);
    inventory[idx] = max(0, inventory[idx] - 1);
    saveData();
  }
  if (checkCollapse(currentFloor)) {
    collapseGame();
    return;
  }

  float closeChance = min(0.05 + currentFloor * 0.01, 0.35);
  if (random(1) < closeChance) {
    closeCallActive = true;
    closeCallTimer = GAME_FPS * 2;
    addCrack();
  } else closeCallActive = false;

  boolean ranOut = !used.equals("WOOD") && inventory[materialIndex(used)] <= 0;
  if (ranOut) {
    selectedMaterial = "WOOD";
    milestoneMessage = "OUT OF " + used + "! SWITCHED TO WOOD";
    milestoneTimer = GAME_FPS * 3;
  } else {
    String message = milestoneFor(currentFloor);
    if (!message.equals("")) {
      milestoneMessage = message;
      milestoneTimer = GAME_FPS * 3;
    }
  }

  if (currentFloor > 0 && currentFloor % 20 == 0) {
    coins += 125;
    statTotalCoinsEarned += 125;
    saveData();
    centerMessage = "FLOOR " + currentFloor + "! YOU GOT +125 COINS";
    centerMessageTimer = GAME_FPS * 3;
  }
  if (currentFloor == 50 && !milestone50Awarded) {
    milestone50Awarded = true;
    centerMessage = "FLOOR 50! YOU GOT A FIND RESOURCES BONUS ROUND";
    centerMessageTimer = GAME_FPS * 3;
    triggerBonusFarm();
  }
}

int computeGreedScore(boolean collapsed) {
  int score = min(currentFloor * 2, 60);
  if (!collapsed) score += 10;
  if (selectedMaterial.equals("WOOD") && currentFloor >= 10) score += 10;
  score = constrain(score, 0, 100);
  greedLabel = score <= 20 ? "CAREFUL" : score <= 40 ? "CAUTIOUS" : score <= 60 ? "RISK TAKER" : score <= 80 ? "GREEDY" : "EXTREMELY GREEDY";
  return score;
}

void stopGame() {
  statTotalAttempts++;
  statTotalStops++;
  if (currentFloor > bestFloor) {
    bestFloor = currentFloor;
  }
  lastRoundFloor = currentFloor;
  lastRoundResult = "STOPPED";
  lastRoundMaterial = selectedMaterial;
  greedScore = computeGreedScore(false);
  currentState = STOPPED;
  saveData();
}

void collapseGame() {
  statTotalAttempts++;
  statTotalCollapses++;
  lastRoundFloor = currentFloor;
  lastRoundResult = "COLLAPSED";
  lastRoundMaterial = selectedMaterial;
  greedScore = computeGreedScore(true);
  currentState = COLLAPSED;
  saveData();
}

void updateGame() {
  if (currentState.equals(FARM) || currentState.equals(BONUS_FARM)) updateFarm();
  if (milestoneTimer > 0) milestoneTimer--;
  if (centerMessageTimer > 0) centerMessageTimer--;
  if (closeCallTimer > 0) {
    closeCallTimer--;
    if (closeCallTimer == 0) closeCallActive = false;
  }
  if (shopMessageTimer > 0) shopMessageTimer--;
}

int materialIndex(String material) {
  for (int i = 0; i < MATERIALS.length; i++) if (MATERIALS[i].equals(material)) return i;
  return 0;
}

void loadData() {
  File file = new File(saveFile);
  if (!file.exists()) return;
  try {
    JSONObject data = loadJSONObject(saveFile);
    if (data == null) return;
    coins = data.getInt("coins", coins);
    bestFloor = data.getInt("best_floor", bestFloor);
    JSONObject savedInventory = data.getJSONObject("inventory");
    if (savedInventory != null) {
      for (int i = 1; i < inventory.length; i++) inventory[i] = savedInventory.getInt(MATERIALS[i], inventory[i]);
    }
    JSONObject stats = data.getJSONObject("stats");
    if (stats != null) {
      statHighestAttempt = stats.getInt("highest_attempt", statHighestAttempt);
      statTotalAttempts = stats.getInt("total_attempts", statTotalAttempts);
      statTotalCollapses = stats.getInt("total_collapses", statTotalCollapses);
      statTotalStops = stats.getInt("total_stops", statTotalStops);
      statTotalFloorsBuilt = stats.getInt("total_floors_built", statTotalFloorsBuilt);
      statTotalCoinsEarned = stats.getInt("total_coins_earned", statTotalCoinsEarned);
    }
  } catch (RuntimeException e) {
    println("Could not load save data: " + e.getMessage());
  }
}

void saveData() {
  try {
    JSONObject data = new JSONObject();
    data.setInt("coins", coins);
    data.setInt("best_floor", bestFloor);
    JSONObject savedInventory = new JSONObject();
    for (int i = 1; i < inventory.length; i++) savedInventory.setInt(MATERIALS[i], inventory[i]);
    data.setJSONObject("inventory", savedInventory);
    JSONObject stats = new JSONObject();
    stats.setInt("best_floor", bestFloor);
    stats.setInt("highest_attempt", statHighestAttempt);
    stats.setInt("total_attempts", statTotalAttempts);
    stats.setInt("total_collapses", statTotalCollapses);
    stats.setInt("total_stops", statTotalStops);
    stats.setInt("total_floors_built", statTotalFloorsBuilt);
    stats.setInt("total_coins_earned", statTotalCoinsEarned);
    data.setJSONObject("stats", stats);
    saveJSONObject(data, saveFile);
  } catch (RuntimeException e) {
    println("Could not save data: " + e.getMessage());
  }
}

class HitBox {
  float x, y, w, h;
  HitBox(float x, float y, float w, float h) {
    this.x = x;
    this.y = y;
    this.w = w;
    this.h = h;
  }
  boolean contains(float px, float py) {
    return px >= x && px <= x + w && py >= y && py <= y + h;
  }
}

class FallingItem {
  float x, y, speed;
  int size, value;
  boolean isCoin;
  String material;
  FallingItem(float x, float y, float speed, int size, boolean isCoin, String material, int value) {
    this.x = x;
    this.y = y;
    this.speed = speed;
    this.size = size;
    this.isCoin = isCoin;
    this.material = material;
    this.value = value;
  }
}

class Crack {
  int floorIndex, offsetX, offsetY;
  Crack(int floorIndex, int offsetX, int offsetY) {
    this.floorIndex = floorIndex;
    this.offsetX = offsetX;
    this.offsetY = offsetY;
  }
}