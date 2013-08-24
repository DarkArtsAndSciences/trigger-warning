package {
	import flash.display.MovieClip;
	import flash.events.*;
	import flash.geom.Point;

	public class Boid extends MovieClip {
		static var boids = [];
		var velocity:Point;
		var maxSpeed = 100;

		public function Boid() {
			boids.push(this);
			x = 100 + Math.random() * 600;
			y = 100 + Math.random() * 400;
			velocity = new Point(0,0);
			addEventListener(Event.ENTER_FRAME, onEnterFrame);
		}

		function onEnterFrame(e:Event):void {
			var r1 = rule1(this);
			var r2 = rule2(this, 50);
			var r3 = rule3(this, 200);
			var r4 = rule4(this, 1);
			var r = r1.add(r2.add(r3.add(r4)))

			velocity = velocity.add(r);
			var speed = Point.distance(velocity, new Point);
			if (speed > maxSpeed) {
				velocity = new Point(velocity.x/speed, velocity.y/speed);
				velocity.normalize(maxSpeed);
				velocity.offset(-r2.x, -r2.y);
			}
			x += velocity.x / 10;
			y += velocity.y / 10;
		}

		// Rule 1: Boids try to fly towards the centre of mass of neighbouring boids.
		function rule1(b:Boid):Point {
			var rule1 = new Point();
			for (var i in boids) {
				if (b == boids[i]) continue;
				rule1.offset(boids[i].x, boids[i].y);
			}
			var n = boids.length - 1;
			return new Point((rule1.x/n - b.x)/200, (rule1.y/n - b.y)/200);
		}

		// Rule 2: Boids try to keep a small distance away from other objects (including other boids).
		function rule2(b:Boid, minDistance:Number):Point {
			var rule2 = new Point();
			var pb = new Point(b.x, b.y);
			for (var i in boids) {
				if (b == boids[i]) continue;
				var pb2 = new Point(boids[i].x, boids[i].y);
				if (Point.distance(pb, pb2) < minDistance) {
					rule2 = rule2.add(pb2).subtract(pb);
				}
			}
			return rule2;
		}

		// Rule 3: Boids try to match velocity with near boids.
		function rule3(b:Boid, minDistance:Number):Point {
			var rule3 = new Point();
			var pb = new Point(b.x, b.y);
			for (var i in boids) {
				if (b == boids[i]) continue;
				var pb2 = new Point(boids[i].x, boids[i].y);
				if (Point.distance(pb, pb2) < minDistance) {
					rule3 = rule3.add(boids[i].velocity);
				}
			}

			var n = boids.length-1;
			rule3 = new Point(rule3.x/n, rule3.y/n);
			rule3 = rule3.subtract(b.velocity);
			rule3 = new Point(rule3.x/8, rule3.y/8);
			return rule3;
		}

		// Rule 4: Boids try to fly towards the mouse.
		function rule4(b:Boid, speed:Number):Point {
			var rule4 = new Point(mouseX+400, mouseY+300);
			rule4.offset(-b.x, -b.y);
			rule4 = new Point(rule4.x/speed, rule4.y/speed);
			return rule4;
		}
	}
}
