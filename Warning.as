package {
	import flash.media.Sound;

	public class Warning {
		var action:Function;
		var text:String;
		var sound:Sound;

		public function Warning(action:Function, sound:Sound, text:String) {
			this.action = action;
			this.sound = sound;
			this.text = text;
		}

		public function warn() {
			trace(text);
			sound.play();
			action();
		}
	}
}
