package {

	public class Warning {
		var warningText:String;
		var warningFunction:Function;

		public function Warning(warningText:String, warningFunction:Function) {
			this.warningText = warningText;
			this.warningFunction = warningFunction;
		}

		public function warn() {
			trace(warningText);
			warningFunction();
		}
	}
}
