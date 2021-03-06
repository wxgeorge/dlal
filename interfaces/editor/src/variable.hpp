#ifndef VARIABLE_HPP_INCLUDED
#define VARIABLE_HPP_INCLUDED

#include "globals.hpp"
#include "object.hpp"

#include <wrapper.hpp>

#include <string>

#include <obvious.hpp>

struct Variable: public Object {
	Variable& name(std::string s){ _name=s; return *this; }
	Variable& value(std::string s){ _value=s; return *this; }

	void draw(bool selected) const {
		dans_sfml_wrapper_text_draw(mouseX(), mouseY(), SZ, text().c_str(), 0, 255, selected?255:0, 255);
	}

	bool contains(int mouseX, int mouseY) const {
		return
			this->mouseX()<mouseX&&mouseX<this->mouseX()+dans_sfml_wrapper_text_width(SZ, text().c_str())
			&&
			this->mouseY()<mouseY&&mouseY<this->mouseY()+SZ;
	}

	std::string text() const { return _name+": "+_value; }

	std::string _name, _value;
};

std::ostream& operator<<(std::ostream& o, const Variable& v){
	return o<<v.text();
}

#endif
