package {
	import flash.display.MovieClip;
	import flash.events.*;
	import flash.geom.Point;

	public class Boid extends MovieClip {
		static var boids = [];
		var location:Point;  // convenience for x,y
		var velocity:Point;

		// moods
		var startled = false;
		var startleOffset:Point;
		var anger = 0.0;		// red
		var fear = 0.0;			// blue
		var fatigue = 0.0;		// alpha
		var infection = 0.0;	// green

		public function Boid() {
			boids.push(this);

			x = 100 + Math.random() * 600;
			y = 100 + Math.random() * 400;
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
			// calculate new velocity
			velocity = velocity.add(rules());

			// tired birds have a lower max speed
			var speed = Point.distance(velocity, new Point());
			var maxSpeed = 20*(1-fatigue);  // pixels per frame?
			if (speed > maxSpeed) {  // flying too fast
				// slow down
				velocity.x /= speed;
				velocity.y /= speed;
				velocity.normalize((speed+maxSpeed)/2);

				// increase fatigue
				fatigue += 1/300;
				if (fatigue > 1) fatigue = 1;
			}

			// tired birds drift down
			velocity.y += Math.abs(velocity.y) * fatigue / 2;

			// set velocity, location, and rotation
			setVelocity(velocity.x, velocity.y);

			// set color based on mood
			var tint = transform.colorTransform;
			tint.redOffset   = 255*anger;
			tint.greenOffset = 255*infection;
			tint.blueOffset  = 255*fear;
			transform.colorTransform = tint;

			// tired birds fade out
			alpha = 1-fatigue;
		}

		// Basic flocking rules from http://www.kfish.org/boids/pseudocode.html
		function rules():Point {
			var rule1 = new Point();
			var rule2 = new Point();
			var rule3 = new Point();
			for (var i in boids) {
				if (this == boids[i]) continue;
				rule1.offset(boids[i].x, boids[i].y);
				var distance = Point.distance(location, boids[i].location)
				if (distance < 30)
					rule2 = rule2.add(location.subtract(boids[i].location));
				if (distance < 300)
					rule3 = rule3.add(boids[i].velocity);
			}
			var n = boids.length - 1;
			rule1 = startled ? startleOffset : new Point((rule1.x/n - x)/200, (rule1.y/n - y)/200);
			rule3 = new Point((rule3.x/n - velocity.x)/8,
							  (rule3.y/n - velocity.y)/8);

			return rule1.add(rule2).add(rule3).add(rule4(0.01)).add(rule5(1));
		}

		// Boids try to fly towards the mouse.
		function rule4(scale:Number):Point {
			return new Point((mouseX+400-x)*scale, (mouseY+300-y)*scale);
		}

		// Boids try to stay on screen.
		function rule5(amount:Number):Point {
			var rule5 = new Point();
			var xmin = 0;
			var xmax = 800;
			var ymin = 0;
			var ymax = 600;
			if (x < xmin) rule5.x = amount;
			if (x > xmax) rule5.x = -amount;
			if (y < ymin) rule5.y = amount;
			if (y > ymax) rule5.y = -amount;
			return rule5;
		}

		static function startle(location:Point, range:Number, amount:Number):void {
			//trace("startle at " + location);
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
