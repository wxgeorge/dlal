#include <SFML/Graphics.hpp>

#include <string>
#include <set>
#include <list>
#include <map>
#include <vector>

class Component{
	public:
		enum Type{
			OTHER,
			AUDIO,
			BUFFER,
			COMMANDER,
			LINER,
			MIDI,
			NETWORK
		};
		struct Connection{
			Connection(){}
			Connection(Component& component): _component(&component), _on(true), _heat(0.0f) {}
			Component* _component;
			bool _on;
			float _heat;
		};
		Component();
		Component(std::string name, std::string type);
		void renderLines(sf::VertexArray&);
		void renderText(sf::RenderWindow&, const sf::Font&);
		std::string _name, _label;
		Type _type;
		float _phase, _heat;
		std::map<std::string, Connection> _connections;
		std::set<Component*> _connecters;
		int _x, _y;
		bool _laidout;
};

class Viewer{
	public:
		Viewer();
		void process(std::string);
		void render(sf::RenderWindow& windowVis, sf::RenderWindow& windowTxt);
	private:
		void layout();
		sf::Font _font;
		std::list<std::string> _reports;
		std::map<std::string, Component> _nameToComponent;
		std::vector<std::pair<std::string, std::string>> _pendingConnections;
		std::map<std::string, std::string> _variables;
		unsigned _w, _h;
};
