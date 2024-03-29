package {
	import flash.display.*;
	import flash.events.*;
	import flash.geom.Point;
	import flash.utils.*;

	// Basic flocking rules from http://www.kfish.org/boids/pseudocode.html

	public class Boid extends MovieClip {
		private static var game:Game;

		static var boids = [];
		var location:Point;  // convenience for x,y
		var velocity:Point;

		var follow:Point;
		var avoid:Point;

		var isStartled = false;
		//var startleOffset:Point;
		var startleEndTime = 0;

		var isPerching = false;
		var perchEndTime = 0;

		var anger = 0.0;		// red
		var fear = 0.0;			// blue
		var fatigue = 0.0;		// alpha
		var infection = 0.0;	// green


		public function Boid() {
			boids.push(this);

			x = Math.random() * 800;
			y = Math.random() * 600;
			location = new Point(x,y);
			velocity = new Point(0,0);
			//startleOffset = new Point(0,0);

			addEventListener(Event.ENTER_FRAME, onEnterFrame);
		}

		public static function registerGame(g:Game) {
			game = g;
		}

		function setVelocity(x:Number, y:Number) {
			velocity.x = x;
			velocity.y = y;
			rotation = Math.atan2(velocity.y,velocity.x)*180/Math.PI;
			this.x += x;
			this.y += y;
			location = new Point(this.x, this.y);
		}

		function setAnger(value:Number) {
			anger = Math.max(Math.min(value, 1), 0);
		}

		function setFear(value:Number) {
			fear = Math.max(Math.min(value, 1), 0);
		}

		function setFatigue(value:Number) {
			fatigue = Math.max(Math.min(value, 1), 0);
		}

		function onEnterFrame(e:Event):void {
			// set color based on mood
			var tint = transform.colorTransform;
			tint.redOffset   = 255*anger;
			tint.greenOffset = 255*fatigue;
			tint.blueOffset  = 255*fear;
			transform.colorTransform = tint;

			// sick birds fade out
			alpha = 1-infection;

			// perching
			var groundLevel = stage.height - 10;
			if (y > groundLevel) {
				// start perching
				if (!isPerching && (fatigue || anger || fear)) {
					isPerching = true;
					perchEndTime = getTimer()+10000;
				}
				y = groundLevel;
				rotation = 90;
			}
			if (isPerching) {
				if ((perchEndTime > getTimer()) || (fatigue || anger || fear)) {
					// still perching
					setFatigue(fatigue - Game.perFrame);
					setAnger(anger - Game.perFrame);
					setFear(fear - Game.perFrame);
					return;  // don't move
				} else {
					// done perching
					isPerching = false;
					velocity.x = 0;
					velocity.y = -2;
				}
			}

			// flying
			var speed = Point.distance(velocity, new Point());
			var maxSpeed = 10*(1-fatigue);  // tired birds have a lower max speed
			if (speed > maxSpeed) {  // flying too fast
				// slow down
				velocity.x /= speed;
				velocity.y /= speed;
				velocity.normalize(maxSpeed);

				// increase fatigue
				setFatigue(fatigue + Game.perFrame);

				// increase fear, more at higher speeds
				setFear(fear + Game.perFrame*(speed - maxSpeed));

			} else if (speed < maxSpeed/3) { // flying very slow
				// decrease fatigue
				setFatigue(fatigue - Game.perFrame);
			}

			// calculate flocking
			var towardsFlock = new Point();
			var avoidCollision = new Point();
			var matchVelocity = new Point();
			var flyingBoids = 0;
			var nearBoids = 0;
			for (var i in boids) {
				if (this == boids[i]) continue;
				var distance = Point.distance(location, boids[i].location)

				if (!boids[i].isPerching) {
					flyingBoids++;

					// move towards the center of the flying flock
					towardsFlock.offset(boids[i].x, boids[i].y);

					// match velocity with nearby boids
					if (distance < stage.width/2) {
						nearBoids++;
						matchVelocity = matchVelocity.add(boids[i].velocity);
					}
				}

				// avoid collisions with nearby boids
				if (distance < width*3) {
					if (anger <= boids[i].anger) {
						avoidCollision = avoidCollision.add(location.subtract(boids[i].location));
						setAnger(anger + Game.perFrame*10);
					} else {
						boids[i].setFear(boids[i].fear + Game.perFrame*10);
					}
				}
			}

			// startled boids ignore the flock and fly away from the startle location
			if (isStartled) {
				if (startleEndTime < getTimer()) {
					isStartled = false;
					avoid = null;
					setFear(fear/2);
					//velocity = velocity.subtract(startleOffset);
				} else {
					towardsFlock = towards(location, avoid, 1/200);
				}
			}

			// calculate center of flock
			if (!isStartled && flyingBoids) {
				towardsFlock.x /= flyingBoids;
				towardsFlock.y /= flyingBoids;
				towardsFlock = towards(location, towardsFlock, 1/200);
			}

			// calculate average velocity
			if (nearBoids) {
				matchVelocity.x /= nearBoids;
				matchVelocity.y /= nearBoids;
				matchVelocity = towards(velocity, matchVelocity, 1/8);
			}

			// add up offsets
			velocity = velocity.add(towardsFlock);
			velocity = velocity.add(avoidCollision);
			velocity = velocity.add(matchVelocity);
			velocity = velocity.add(towardsMouse(1/100));
			velocity = velocity.add(stayOnScreen(5));
			velocity = velocity.add(towards(location, avoid, -1/100));

			// set velocity, location, and rotation
			setVelocity(velocity.x, velocity.y);

			// tired birds drift down
			if (fatigue > 1/2) {
				y += fatigue * Game.perFrame * stage.height;
			}
		}

		function towards(start:Point, end:Point, distance:Number):Point {
			if (!(start && end && distance)) return new Point();
			return new Point((end.x-start.x)*distance, (end.y-start.y)*distance);
		}

		function towardsMouse(scale:Number):Point {
			if (Game(parent).isMouseDown) return towards(location, new Point(stage.mouseX, stage.mouseY), scale);
			return new Point();
		}

		function stayOnScreen(amount:Number):Point {
			var point = new Point();
			var border = 10;
			var xmin = border;
			var xmax = stage.width - border;
			var ymin = border;
			var ymax = stage.height - border;
			if (x < xmin) point.x = amount;
			if (x > xmax) point.x = -amount;
			if (y < ymin) point.y = amount;
			if (y > ymax) point.y = -amount;
			return point;
		}

		static function startle(location:Point, range:Number, amount:Number, fear:Number):void {
			for (var i in boids) {
				var distance = Point.distance(location, boids[i].location);
				if (distance < range) {
					// startle this boid
					boids[i].isStartled = true;
					boids[i].startleEndTime = getTimer()+10000;

					// scare this boid
					boids[i].setFear(boids[i].fear + fear);

					// fly away from the location
					var offset = location.subtract(boids[i].location);
					var angle = Math.atan2(offset.x, offset.y);
					var speed = Math.pow(range-distance,1.5)/range * amount;
					var offset2 = new Point(0 - Math.sin(angle) * speed,
											0 - Math.cos(angle) * speed);
					//boids[i].startleOffset = offset2;
					boids[i].avoid = location;

					// use setVelocity's side effects, but keep the old velocity
					var oldVelocity = boids[i].velocity;
					boids[i].setVelocity(offset2.x, offset2.y);
					boids[i].velocity = oldVelocity;
				}
			}
		}
	}
}
