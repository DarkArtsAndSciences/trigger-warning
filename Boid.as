package {
	import flash.display.MovieClip;
	import flash.events.*;
	import flash.geom.Point;
	import flash.utils.*;

	public class Boid extends MovieClip {
		static var boids = [];
		var location:Point;  // convenience for x,y
		var velocity:Point;

		// moods
		var startled = false;
		var startleOffset:Point;
		var isPerching = false;
		var perchEndTime = 0;
		var anger = 0.0;		// red
		var fear = 0.0;			// blue
		var fatigue = 0.0;		// alpha
		var infection = 0.0;	// green

		// If you increment once per frame by this number, it takes 10 seconds to go from 0.0 to 1.0.
		static var frameIncrement = 1/300;  // 1/framerate * 1/10

		public function Boid() {
			boids.push(this);

			x = Math.random() * 800;
			y = Math.random() * 600;
			location = new Point(x,y);
			velocity = new Point(0,0);
			startleOffset = new Point(0,0);

			addEventListener(Event.ENTER_FRAME, onEnterFrame);
		}

		function setVelocity(x:Number, y:Number) {
			velocity.x = x;
			velocity.y = y;
			rotation = Math.atan2(velocity.y,velocity.x)*180/Math.PI;
			this.x += x;
			this.y += y;
			location = new Point(this.x, this.y);
		}

		function onEnterFrame(e:Event):void {
			// set color based on mood
			var tint = transform.colorTransform;
			tint.redOffset   = 255*anger;
			tint.greenOffset = 255*infection;
			tint.blueOffset  = 255*fear;
			transform.colorTransform = tint;

			// tired birds fade out
			alpha = 1-fatigue;

			// perching
			var groundLevel = stage.height - 10;
			if (y > groundLevel) {
				// start perching
				if (!isPerching) {
					isPerching = true;
					perchEndTime = getTimer()+10000;
				}
				y = groundLevel;
				rotation = 90;
			}
			if (isPerching) {
				if (perchEndTime > getTimer()) {
					// still perching
					fatigue = Math.max(fatigue - frameIncrement, 0);
					anger = Math.max(anger - frameIncrement, 0);
					fear = Math.max(fear - frameIncrement, 0);
					return;  // don't move
				} else {
					// done perching
					isPerching = false;
					velocity.y -= 20;
				}
			}

			// calculate new velocity
			velocity = velocity.add(rules());

			// tired birds have a lower max speed
			var speed = Point.distance(velocity, new Point());
			var maxSpeed = 10*(1-fatigue);  // pixels per frame?

			if (speed > maxSpeed) {  // flying too fast
				// slow down
				velocity.x /= speed;
				velocity.y /= speed;
				velocity.normalize((speed+maxSpeed)/2);

				// increase fatigue
				fatigue = Math.max(fatigue + frameIncrement, 0);

			} else if (speed < maxSpeed/3) { // flying very slow
				// decrease fatigue
				fatigue = Math.max(fatigue - frameIncrement, 0);
			}

			// tired birds drift down
			velocity.y += Math.abs(velocity.y) * fatigue / 2;

			// set velocity, location, and rotation
			setVelocity(velocity.x, velocity.y);
		}

		// Basic flocking rules from http://www.kfish.org/boids/pseudocode.html
		function rules():Point {
			var towardsFlock = new Point();
			var avoidCollision = new Point();
			var matchVelocity = new Point();

			for (var i in boids) {
				if (this == boids[i]) continue;
				towardsFlock.offset(boids[i].x, boids[i].y);
				var distance = Point.distance(location, boids[i].location)
				if (distance < stage.height/20)
					avoidCollision = avoidCollision.add(location.subtract(boids[i].location));
				if (distance < stage.height/2)
					matchVelocity = matchVelocity.add(boids[i].velocity);
			}

			var n = boids.length - 1;
			towardsFlock = startled ? startleOffset : new Point((towardsFlock.x/n - x)/200, (towardsFlock.y/n - y)/200);
			matchVelocity = new Point((matchVelocity.x/n - velocity.x)/8,
							  (matchVelocity.y/n - velocity.y)/8);

			var point = new Point();
			point = towardsFlock.add(avoidCollision).add(matchVelocity);
			point = point.add(towardsMouse(1/100));
			point = point.add(stayOnScreen(5));
			return point;
		}

		function towardsMouse(scale:Number):Point {
			if (Game(parent).isMouseDown) {
				var px = stage.mouseX - x;
				var py = stage.mouseY - y;
				return new Point(px*scale, py*scale);
			}
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

		static function startle(location:Point, range:Number, amount:Number):void {
			for (var i in boids) {
				var distance = Point.distance(location, boids[i].location);
				if (distance < range) {
					// startle this boid
					boids[i].startled = true;
					boids[i].anger += 0.1;

					// fly away from the location
					var offset = location.subtract(boids[i].location);
					var angle = Math.atan2(offset.x, offset.y);
					var speed = Math.pow(range-distance,1.5)/range * amount;
					var offset2 = new Point(0 - Math.sin(angle) * speed,
											0 - Math.cos(angle) * speed);
					boids[i].startleOffset = offset2;

					// use setVelocity's side effects, but keep the old velocity
					var oldVelocity = boids[i].velocity;
					boids[i].setVelocity(offset2.x, offset2.y);
					boids[i].velocity = oldVelocity;
				}
			}
		}
	}
}
