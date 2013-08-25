package {
	import flash.media.Sound;

	public class Warning {
		private static var game:Game;

		var sound:Sound;
		var text:String;
		var action:Function;

		public function Warning(sound:Sound, text:String, action:Function) {
			this.action = action;
			this.sound = sound;
			this.text = text;
		}

		public static function registerGame(g:Game) {
			game = g;
		}

		public function warn(location) {
			//trace(text);
			if (sound) sound.play();
			if (action != null) action(location);
		}
	}
}
