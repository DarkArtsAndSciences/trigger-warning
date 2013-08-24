package {
	import flash.text.TextField;
	import flash.media.Sound;

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
			sound.play();
			action();
		}
	}
}
