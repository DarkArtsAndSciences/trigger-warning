package {
	import flash.display.MovieClip;
	import flash.events.*;
	import flash.geom.Point;

	public class Boid extends MovieClip {
		static var boids = [];
		var location:Point;  // convenience for x,y
		var velocity:Point;

		public function Boid() {
			boids.push(this);

			x = 100 + Math.random() * 600;
			y = 100 + Math.random() * 400;
			location = new Point(x,y);
			velocity = new Point(0,0);

			addEventListener(Event.ENTER_FRAME, onEnterFrame);
		}

		function onEnterFrame(e:Event):void {
			velocity = velocity.add(rules());
			var speed = Point.distance(velocity, new Point);
			var maxSpeed = 25;  // pixels per frame?
			if (speed > maxSpeed) {
				velocity = new Point(velocity.x/speed, velocity.y/speed);
				velocity.normalize(maxSpeed);
			}
			x += velocity.x;
			y += velocity.y;
			location = new Point(x,y);
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
			rule1 = new Point((rule1.x/n - x)/200, (rule1.y/n - y)/200);
			rule3 = new Point((rule3.x/n - velocity.x)/8,
							  (rule3.y/n - velocity.y)/8);

			return rule1.add(rule2).add(rule3).add(rule4(0.005));
		}

		// Boids try to fly towards the mouse.
		function rule4(scale:Number):Point {
			return new Point((mouseX+400-x)*scale, (mouseY+300-y)*scale);
		}
	}
}
