package {
	import flash.text.TextField;
	import flash.media.Sound;
	import flash.events.TimerEvent;
	import flash.utils.Timer;

	public class Warning {
		var action:Function;
		var text:String;
		var sound:Sound;
		var warningText:TextField;

		public function Warning(action:Function, sound:Sound, text:String, warningText:TextField) {
			this.action = action;
			this.sound = sound;
			this.text = text;
			this.warningText = warningText;
		}

		public function warn() {
			warningText.text = text;
			warningText.alpha = 1.0;
			var timer = new Timer(100, 100);
			function fade(e:TimerEvent):void {
				warningText.alpha -= 0.01;
			}
			function fadeEnd(e:TimerEvent):void {
				timer.stop();
			}
			timer.addEventListener(TimerEvent.TIMER, fade);
			timer.addEventListener(TimerEvent.TIMER_COMPLETE, fadeEnd);
			timer.start();

			sound.play();
			action();
		}

	}
}
