package {
	import flash.media.Sound;

	public class Warning {
		var sound:Sound;
		var text:String;
		var action:Function;

		public function Warning(sound:Sound, text:String, action:Function) {
			this.action = action;
			this.sound = sound;
			this.text = text;
		}

		public function warn() {
			//trace(text);
			if (sound) sound.play();
			if (action != null) action();
		}

	}
}
